//! Throwaway: not part of ordin.
#![allow(dead_code, unused_imports)]

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::time::Duration;

use ordin_agent_model::testkit::{ContractFixture, InMemorySource};
use ordin_agent_model::{
    read_tree, ModelPart, PartKind, PartSource, RepositoryRef, SourceOverride, SourceScope,
    VocabularySet,
};
use ordin_checker::{check_parts, CheckSubject, Checker, RepositoryCheck};
use ordin_journal::{
    ApplyMode, Datastore, DatastoreConfig, Journal, JournalOptions, MigrationRegistry, SystemClock,
    MIGRATIONS,
};
use ordin_organisation_profile::{
    Clock, OrganisationProfileService, ProfileMode, ProfileOptions, Timestamp,
};
use ordin_resolver::{ResolveRequest, ResolverAndCompiler, ResolverConfig};
use ordin_types::domain::HarnessKind;
use ordin_types::AgentRepositoryId;
use serde_json::{json, Value};

const REPOSITORY_LABEL: &str = "github.com/acme/agents";

fn checks_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("the crate sits two levels below the workspace root")
        .join("testdata")
        .join("parity")
        .join("checks")
}

/// Every file under `dir`, keyed by its '/'-separated path relative to `dir`.
fn read_dir(dir: &Path) -> BTreeMap<String, Vec<u8>> {
    fn walk(base: &Path, dir: &Path, out: &mut BTreeMap<String, Vec<u8>>) {
        let entries = std::fs::read_dir(dir)
            .unwrap_or_else(|e| panic!("fixture folder {} cannot be read: {e}", dir.display()));
        for entry in entries {
            let path = entry.expect("a directory entry").path();
            if path.is_dir() {
                walk(base, &path, out);
            } else {
                let relative = path
                    .strip_prefix(base)
                    .expect("under the base")
                    .components()
                    .map(|c| c.as_os_str().to_string_lossy().into_owned())
                    .collect::<Vec<_>>()
                    .join("/");
                out.insert(relative, std::fs::read(&path).expect("a readable fixture"));
            }
        }
    }
    let mut out = BTreeMap::new();
    walk(dir, dir, &mut out);
    out
}

fn json_file(path: &Path) -> Value {
    let text = std::fs::read_to_string(path)
        .unwrap_or_else(|e| panic!("{} cannot be read: {e}", path.display()));
    serde_json::from_str(&text).unwrap_or_else(|e| panic!("{} is not JSON: {e}", path.display()))
}

/// The case folders of one family, by name; none fails.
fn cases(family: &str) -> Vec<(String, PathBuf)> {
    let root = checks_root();
    assert!(
        root.is_dir(),
        "the parity fixture folder {} is missing",
        root.display()
    );
    let dir = root.join(family).join("cases");
    let mut out: Vec<(String, PathBuf)> = std::fs::read_dir(&dir)
        .unwrap_or_else(|e| panic!("{} cannot be read: {e}", dir.display()))
        .map(|e| e.expect("an entry").path())
        .filter(|p| p.is_dir())
        .map(|p| (p.file_name().unwrap().to_string_lossy().into_owned(), p))
        .collect();
    out.sort();
    assert!(
        !out.is_empty(),
        "the parity fixture folder {} is empty",
        dir.display()
    );
    out
}

/// The catalogue plus the case's tree, read twice as the Agent Model prescribes (the second read
/// with the vocabulary set of the first).
fn parts_of(case: &Path) -> Vec<ModelPart> {
    let mut files = read_dir(&checks_root().join("catalogue"));
    assert!(!files.is_empty(), "the shared catalogue is empty");
    files.extend(read_dir(&case.join("tree")));
    let first = read_tree(&files, &VocabularySet::default());
    let vocabularies: Vec<&ModelPart> = first
        .parts
        .iter()
        .filter(|p| p.kind == PartKind::Vocabulary)
        .collect();
    let set = VocabularySet::from_parts(&vocabularies).expect("one vocabulary part per axis");
    let reading = read_tree(&files, &set);
    assert!(
        reading.refused.is_empty(),
        "{}: the reader refused {:?}",
        case.display(),
        reading
            .refused
            .iter()
            .map(|(p, e)| (p.as_str(), e.code()))
            .collect::<Vec<_>>()
    );
    reading.parts
}

fn acme() -> RepositoryRef {
    RepositoryRef::Repository(AgentRepositoryId(uuid::uuid!(
        "01900000-0000-7000-8000-0000000000a1"
    )))
}

fn scope() -> SourceScope {
    SourceScope {
        home: acme(),
        profile: Vec::new(),
        include_bundled: false,
    }
}

fn source_of(parts: Vec<ModelPart>) -> Arc<dyn PartSource> {
    Arc::new(InMemorySource::new(&ContractFixture {
        repositories: vec![(acme(), REPOSITORY_LABEL.to_owned(), parts)],
        withdrawn: Vec::new(),
        refused: Vec::new(),
    }))
}

struct Now;

impl Clock for Now {
    fn now(&self) -> Timestamp {
        Timestamp::now()
    }
}

/// A Checker over a fresh SQLite journal, the default (empty) trust policy, bound to `source`.
async fn checker(dir: &Path, source: Arc<dyn PartSource>) -> Checker {
    let store = Datastore::open(DatastoreConfig::Sqlite {
        path: dir.join("journal.db"),
        backup_dir: dir.join("backups"),
    })
    .await
    .expect("open the datastore");
    let mut registry = MigrationRegistry::new();
    registry.register(MIGRATIONS).expect("the journal");
    registry
        .register(ordin_checker::migrations())
        .expect("the checker");
    registry
        .apply(&store, ApplyMode::ApplyPending)
        .await
        .expect("migrate");
    let journal = Arc::new(
        Journal::start(
            store,
            JournalOptions {
                automatic_pruning: false,
                prune_interval: Duration::from_secs(3600),
                clock: Arc::new(SystemClock),
            },
        )
        .await
        .expect("start the journal"),
    );
    let resolver = Arc::new(
        ResolverAndCompiler::new(ResolverConfig {
            bundle_root: dir.join("bundles"),
            compiler_version: "0.1.0-test".to_owned(),
        })
        .expect("a resolver"),
    );
    resolver
        .install_part_source(Arc::clone(&source))
        .expect("bind the resolver");
    let profile = Arc::new(
        OrganisationProfileService::start(
            ProfileMode::NotUsed,
            ProfileOptions {
                refresh_interval: Duration::from_secs(3600),
                clock: Arc::new(Now),
            },
        )
        .await
        .expect("the profile service"),
    );
    let checker = Checker::new(resolver, profile, journal);
    checker
        .install_part_source(source)
        .expect("bind the checker");
    checker
}

struct Temp(PathBuf);

impl Temp {
    fn new() -> Temp {
        let dir =
            std::env::temp_dir().join(format!("ordin-checker-parity-{}", uuid::Uuid::now_v7()));
        std::fs::create_dir_all(&dir).expect("a temporary folder");
        Temp(dir)
    }
}

impl Drop for Temp {
    fn drop(&mut self) {
        let _ = std::fs::remove_dir_all(&self.0);
    }
}

fn sorted_codes(codes: impl IntoIterator<Item = String>) -> Vec<String> {
    let mut codes: Vec<String> = codes.into_iter().collect();
    codes.sort();
    codes
}

fn expected_codes(case: &Path) -> Vec<String> {
    let expected = json_file(&case.join("expected.json"));
    sorted_codes(
        expected["codes"]
            .as_array()
            .expect("expected.json has codes")
            .iter()
            .map(|c| c.as_str().expect("a code").to_owned()),
    )
}

fn root_of(case: &Path) -> String {
    json_file(&case.join("case.json"))["root"]
        .as_str()
        .expect("case.json names the root")
        .to_owned()
}

/// Runs every case and reports all the differences together.
fn assert_no_differences(family: &str, differences: Vec<String>) {
    assert!(
        differences.is_empty(),
        "{family}: {} case(s) differ:\n{}",
        differences.len(),
        differences.join("\n")
    );
}


// ---- Throwaway harness (not committed to ordin): checks the bundled-agents repository at
// $ORDIN_AGENTS_DIR with the same Checker calls the parity test uses.

const COORDINATOR: &str = "urn:ordin:default:workspaces:coordinator";
const DOCUMENT_AGENT: &str = "urn:ordin:default:workspaces:document-agent";
const CSPA: &str = "urn:ordin:default:workspaces:cspa-431";

fn agents_files(gate_override: Option<&str>) -> BTreeMap<String, Vec<u8>> {
    let root = PathBuf::from(std::env::var("ORDIN_AGENTS_DIR").expect("ORDIN_AGENTS_DIR"));
    let mut files: BTreeMap<String, Vec<u8>> = read_dir(&root)
        .into_iter()
        .filter(|(k, _)| k.starts_with("models/"))
        .collect();
    if let Some(gate) = gate_override {
        let key = "models/@default/workspaces/coordinator/workspace-profile.yaml";
        let text = String::from_utf8(files[key].clone()).unwrap();
        let changed = text.replace("publishGate: \"urn:ordin:default:evals\"", &format!("publishGate: \"{gate}\""));
        assert_ne!(text, changed, "the gate line was found");
        files.insert(key.to_owned(), changed.into_bytes());
    }
    files
}

fn agents_parts(files: &BTreeMap<String, Vec<u8>>) -> Vec<ModelPart> {
    let first = read_tree(files, &VocabularySet::default());
    let vocabularies: Vec<&ModelPart> = first.parts.iter().filter(|p| p.kind == PartKind::Vocabulary).collect();
    let set = VocabularySet::from_parts(&vocabularies).expect("one vocabulary part per axis");
    let reading = read_tree(files, &set);
    println!("READ parts={} refused={:?} unowned={:?}", reading.parts.len(),
        reading.refused.iter().map(|(p, e)| (p.as_str(), e.code())).collect::<Vec<_>>(), reading.unowned_files);
    assert!(reading.refused.is_empty(), "the reader refused parts");
    reading.parts
}

async fn run_all(label: &str, gate_override: Option<&str>) -> usize {
    let parts = agents_parts(&agents_files(gate_override));
    let mut failures = 0;
    // authoringcheck: the repository read as a whole.
    let temp = Temp::new();
    let checker = checker(&temp.0, source_of(parts.clone())).await;
    let request = RepositoryCheck {
        repository: acme(),
        repository_display_name: "Bundled agents".to_owned(),
        scope: scope(),
        changes: Vec::new(),
        deletions: Vec::new(),
        source: None,
    };
    let report = checker
        .check_repository(&request, CheckSubject::RepositoryRead { repository: REPOSITORY_LABEL.to_owned(), commit: "e270904".repeat(5) + "00000" })
        .await
        .unwrap_or_else(|e| panic!("authoringcheck: {}", e.code()));
    for f in &report.findings {
        println!("[{label}] AUTHORINGCHECK {} {:?} {:?} {}", f.code, f.severity, f.part_identifier, f.detail);
        if f.code != "repository_checked" { failures += 1; }
    }
    for root in [COORDINATOR, DOCUMENT_AGENT, CSPA] {
    // compositioncheck: each agent with its closure.
    let report = checker
        .check_library_item(&scope(), PartKind::WorkspaceProfile, root)
        .await
        .unwrap_or_else(|e| panic!("compositioncheck: {}", e.code()));
    println!("[{label}] COMPOSITIONCHECK {root} {} finding(s)", report.findings.len());
    for f in &report.findings {
        println!("[{label}] COMPOSITIONCHECK {} {:?} {:?} {}", f.code, f.severity, f.part_identifier, f.detail);
        failures += 1;
    }
    // artefactbuild: the Release Builder's package check of each agent.
    let source = source_of(parts.clone());
    let request = ResolveRequest {
        scope: scope(),
        root_id: root.to_owned(),
        root_version: None,
        target_harness: HarnessKind::ClaudeCode,
        workspace_languages: Vec::new(),
        interface_language: "en-GB".to_owned(),
        pack_answers: Vec::new(),
        pack_changes: Vec::new(),
        overlay_changes: Vec::new(),
        replacements: Vec::new(),
        staged: Vec::new(),
        allow_draft_root: false,
        source: Some(SourceOverride(Arc::clone(&source))),
    };
    let report = check_parts(source.as_ref(), &request)
        .await
        .unwrap_or_else(|e| panic!("artefactbuild: {}", e.code()));
    println!("[{label}] ARTEFACTBUILD {root} {} finding(s)", report.findings.len());
    for f in &report.findings {
        println!("[{label}] ARTEFACTBUILD stop={:?} file={:?} entry={:?} {}", f.stop, f.file, f.entry, f.message);
        failures += 1;
    }
    }
    failures
}

#[tokio::test]
async fn bundled_agents_repository_passes_the_checker() {
    let set = run_all("gate=set", None).await;
    let exact = run_all("gate=exact", Some("urn:ordin:default:evals:mode-boundary:plan-centric-loop-refuses-source-edit")).await;
    let ghost = run_all("gate=ghost", Some("urn:ordin:default:evals:ghost")).await;
    let none = run_all("gate=none", Some("")).await;
    println!("SUMMARY set={set} exact={exact} ghost={ghost} none={none}");
    assert!(ghost > 0, "a gate naming no evaluation must fail (control)");
    assert_eq!(none, 0, "no gate");
    assert_eq!(set, 0, "set gate");
    assert_eq!(exact, 0, "exact gate");
}
