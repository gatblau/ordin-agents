//! Throwaway: not part of ordin. Indexes $ORDIN_AGENTS_DIR as the bundled catalogue, as the
//! application does at start, and reports what is offered.
#![allow(dead_code, unused_imports)]

mod support;

use std::path::{Path, PathBuf};

use ordin_agent_model::{PartKind, BUNDLED_REPOSITORY_ID};
use sqlx::Row;
use support::*;

fn copy_tree(from: &Path, to: &Path) {
    for entry in std::fs::read_dir(from).unwrap() {
        let path = entry.unwrap().path();
        let target = to.join(path.file_name().unwrap());
        if path.is_dir() {
            if path.file_name().unwrap() == ".git" {
                continue;
            }
            std::fs::create_dir_all(&target).unwrap();
            copy_tree(&path, &target);
        } else {
            std::fs::copy(&path, &target).unwrap();
        }
    }
}

#[tokio::test(flavor = "multi_thread")]
async fn bundled_agents_repository_is_indexed_and_the_coordinator_offered() {
    let root = PathBuf::from(std::env::var("ORDIN_AGENTS_DIR").expect("ORDIN_AGENTS_DIR"));
    let env = Env::new(&[]).await;
    copy_tree(&root, &env.bundled);
    let stop = tokio_util::sync::CancellationToken::new();
    env.service
        .start(stop.clone())
        .await
        .unwrap_or_else(|e| panic!("start refused the bundled catalogue: {e:?}"));
    let rows = sqlx::query(
        "SELECT p.kind, p.identifier, i.offered, i.not_offered_reason FROM parts p \
         JOIN part_index i ON i.part_id = p.id ORDER BY p.kind, p.identifier",
    )
    .fetch_all(env.pool())
    .await
    .unwrap();
    let mut not_offered = 0;
    for row in &rows {
        let offered: i64 = row.get(2);
        let reason: Option<String> = row.get(3);
        if offered == 0 {
            not_offered += 1;
        }
        println!(
            "INDEXED {} {} offered={} reason={:?}",
            row.get::<String, _>(0),
            row.get::<String, _>(1),
            offered,
            reason
        );
    }
    println!("INDEXED total={} not_offered={}", rows.len(), not_offered);
    let view = env
        .service
        .find_part(
            BUNDLED_REPOSITORY_ID,
            PartKind::WorkspaceProfile,
            "urn:ordin:default:workspaces:coordinator",
            None,
        )
        .await
        .unwrap_or_else(|e| panic!("find_part: {e:?}"));
    println!(
        "COORDINATOR offered={} state={:?} from={} version={} uses={}",
        view.offered,
        view.state_label,
        view.from,
        view.part.version,
        view.part.uses.len()
    );
    assert!(view.offered, "the coordinator is offered");
    let doc = env
        .service
        .find_part(
            BUNDLED_REPOSITORY_ID,
            PartKind::WorkspaceProfile,
            "urn:ordin:default:workspaces:document-agent",
            None,
        )
        .await
        .unwrap_or_else(|e| panic!("find_part document agent: {e:?}"));
    println!("DOCUMENT_AGENT offered={} uses={}", doc.offered, doc.part.uses.len());
    assert!(doc.offered, "the document agent is offered");
    let cspa = env
        .service
        .find_part(
            BUNDLED_REPOSITORY_ID,
            PartKind::WorkspaceProfile,
            "urn:ordin:default:workspaces:cspa-431",
            None,
        )
        .await
        .unwrap_or_else(|e| panic!("find_part cspa-431: {e:?}"));
    println!("CSPA offered={} uses={}", cspa.offered, cspa.part.uses.len());
    assert!(cspa.offered, "cspa-431 is offered");
    assert_eq!(not_offered, 0, "every part is offered");
    stop.cancel();
}
