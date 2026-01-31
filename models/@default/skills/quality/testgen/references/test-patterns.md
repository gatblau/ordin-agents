# Test generation patterns

Match the project's existing patterns first (inspect any existing `_test.go` or equivalent). Only fall back to these defaults if there are no existing tests to learn from.

## Go — table-driven unit test

```go
func TestProcessRequest_Validation(t *testing.T) {
    tests := []struct {
        name    string
        input   *Request
        wantErr error
    }{
        {
            name:    "nil input returns ErrNilInput",
            input:   nil,
            wantErr: ErrNilInput,
        },
        {
            name:    "empty user ID returns ErrValidation",
            input:   &Request{UserID: ""},
            wantErr: ErrValidation,
        },
        {
            name:    "valid input succeeds",
            input:   &Request{UserID: "u_123", Body: "hello"},
            wantErr: nil,
        },
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            svc := newTestService(t)
            _, err := svc.ProcessRequest(context.Background(), tt.input)
            if !errors.Is(err, tt.wantErr) {
                t.Fatalf("want %v, got %v", tt.wantErr, err)
            }
        })
    }
}
```

Rules:
- Use `errors.Is` for error comparison, not `==` or string contains.
- Sub-test names as short phrases describing the case, not jargon.
- Factory helper `newTestService(t)` lives in `testutil_test.go` if shared across files.

## Go — hand-written mock

```go
type mockDB struct {
    getByIDFunc func(ctx context.Context, id string) (*User, error)
    insertFunc  func(ctx context.Context, u *User) error
}

func (m *mockDB) GetByID(ctx context.Context, id string) (*User, error) {
    if m.getByIDFunc == nil {
        return nil, errors.New("mockDB.GetByID not set")
    }
    return m.getByIDFunc(ctx, id)
}

func (m *mockDB) Insert(ctx context.Context, u *User) error {
    if m.insertFunc == nil {
        return errors.New("mockDB.Insert not set")
    }
    return m.insertFunc(ctx, u)
}
```

Rules:
- Function-field mocks over strict mock libraries. Easier to read.
- Unset methods panic with a clear message.
- One `mock<Interface>` per interface, reused across tests.
- Do not introduce gomock/mockery unless the project already uses them.

## Go — integration test with testcontainers

```go
//go:build integration

package user

func TestUserRepository_CreateAndFetch_Integration(t *testing.T) {
    ctx := context.Background()

    pgContainer, err := postgres.Run(ctx, "postgres:16-alpine",
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("test"),
        postgres.WithPassword("test"),
    )
    if err != nil {
        t.Fatalf("start postgres: %v", err)
    }
    t.Cleanup(func() { _ = pgContainer.Terminate(ctx) })

    dsn, err := pgContainer.ConnectionString(ctx, "sslmode=disable")
    if err != nil {
        t.Fatalf("dsn: %v", err)
    }

    pool, err := pgxpool.New(ctx, dsn)
    if err != nil {
        t.Fatalf("pool: %v", err)
    }
    t.Cleanup(pool.Close)

    // Apply migrations — use the project's migration runner.
    if err := applyMigrations(ctx, pool); err != nil {
        t.Fatalf("migrate: %v", err)
    }

    repo := NewUserRepository(pool)

    u := &User{ID: "u_1", Name: "Alice"}
    if err := repo.Create(ctx, u); err != nil {
        t.Fatalf("create: %v", err)
    }

    got, err := repo.GetByID(ctx, "u_1")
    if err != nil {
        t.Fatalf("get: %v", err)
    }
    if got.Name != "Alice" {
        t.Fatalf("want Alice, got %s", got.Name)
    }
}
```

Rules:
- Build tag `integration` on every integration test — keeps the default `go test` fast.
- Use `t.Cleanup` not `defer` — runs even on test failure.
- Apply migrations in-test, do not assume pre-applied state.
- Never hardcode connection strings; always read from the container.

## Python — pytest parametrize

```python
import pytest

@pytest.mark.parametrize("user_id,body,want_error", [
    ("",      "hi",   ValidationError),
    ("u_123", "",     ValidationError),
    ("u_123", "hi",   None),
])
def test_process_request_validation(user_id, body, want_error):
    svc = make_service()
    if want_error:
        with pytest.raises(want_error):
            svc.process_request(user_id=user_id, body=body)
    else:
        result = svc.process_request(user_id=user_id, body=body)
        assert result is not None
```

## TypeScript — Jest/Vitest it.each

```typescript
describe("processRequest", () => {
  it.each([
    { name: "empty id",  input: { id: "", body: "hi" },  want: "ValidationError" },
    { name: "empty body", input: { id: "u_1", body: "" }, want: "ValidationError" },
    { name: "valid",      input: { id: "u_1", body: "hi" }, want: null },
  ])("$name", async ({ input, want }) => {
    const svc = makeService();
    if (want) {
      await expect(svc.processRequest(input)).rejects.toThrow(want);
    } else {
      await expect(svc.processRequest(input)).resolves.toBeDefined();
    }
  });
});
```

## Rust — rstest parametrization

```rust
#[rstest]
#[case("", "hi", Some(Error::Validation))]
#[case("u_1", "", Some(Error::Validation))]
#[case("u_1", "hi", None)]
fn process_request_validation(#[case] id: &str, #[case] body: &str, #[case] want: Option<Error>) {
    let svc = make_service();
    match (svc.process_request(id, body), want) {
        (Ok(_), None) => {},
        (Err(e), Some(ref w)) if std::mem::discriminant(&e) == std::mem::discriminant(w) => {},
        (got, want) => panic!("mismatch: got {:?}, want {:?}", got, want),
    }
}
```

## Stub service — when test containers are not feasible

Use a stub when the integrating service genuinely cannot be containerised — proprietary appliance, third-party SaaS, hardware peripheral, licensed image you cannot ship. The stub must honour the same wire contract as the real service.

```go
//go:build integration

package appliance

// stubApplianceServer answers the same wire protocol as the real device.
// Contract source: docs/spec/components/Appliance.md §"Command channel" (schema v3).
type stubApplianceServer struct {
    addr     string
    received chan ApplianceCommand
}

func newStubApplianceServer(t *testing.T) *stubApplianceServer {
    t.Helper()
    s := &stubApplianceServer{received: make(chan ApplianceCommand, 16)}
    ln, err := net.Listen("tcp", "127.0.0.1:0")
    if err != nil {
        t.Fatalf("listen: %v", err)
    }
    s.addr = ln.Addr().String()
    go s.serve(ln)
    t.Cleanup(func() { _ = ln.Close() })
    return s
}

func (s *stubApplianceServer) serve(ln net.Listener) { /* … minimal protocol … */ }
```

Rules:
- **Record the contract source** in a comment on the stub type — the spec section, the vendor doc, or the captured trace it was modelled on. Without this, the stub is unverifiable.
- The stub is deterministic. No clock, no randomness unless the contract requires it.
- The stub lives next to the integration test, under the same `integration` build tag (or equivalent).
- Never silently switch to a stub when a test container would have worked. The choice is recorded in the plan and approved by the user.

## Tooling choice — stop and ask

Before generating an integration test, identify which integrating services the function under test crosses (DB, message bus, blob store, external API, peripheral). For each:

1. If the active Practice Pack mandates a specific test-container or stub framework → use it.
2. Else if the project already uses a specific framework in existing tests (detected by reading `go.mod` / `package.json` / `pyproject.toml` and any existing integration tests) → match it.
3. Else → **stop and ask the user**, offering 1–2 concrete recommendations for the language and the services in play. Do not pick silently.

## Fixtures and helpers

Place in `testutil_test.go` (Go), `conftest.py` (Python), `test/fixtures.ts` (TS), `tests/common/mod.rs` (Rust) — only when used in two or more test files. Single-use helpers stay inline.

## Skip pattern — suspected bug

```go
func TestProcessRequest_NegativeCount(t *testing.T) {
    t.Skip("suspected bug: ProcessRequest returns nil instead of ErrValidation for negative count; verify with /rca before enabling")
    // Test body preserved for when the bug is confirmed/fixed.
}
```

Rules:
- Always give a reason in `t.Skip` explaining *what* was unexpected.
- Point the user at `/rca` in the skip message.
- Do not delete the test body — a fix later needs it.
