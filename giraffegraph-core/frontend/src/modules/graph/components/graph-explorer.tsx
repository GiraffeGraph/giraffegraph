"use client";

import { useEffect, useState } from "react";

import {
  getGraphNodeDetail,
  getGraphRelationDetail,
  loadGraphSnapshot,
} from "@/modules/projects/api";
import type {
  CanonicalNodeDetailRecord,
  CanonicalNodeRecord,
  CanonicalRelationDetailRecord,
  CanonicalRelationRecord,
  CanonicalSegmentSupportRecord,
  CanonicalSourceUnitRefRecord,
  GraphSnapshot,
  ProjectRecord,
} from "@/modules/projects/types";
import { formatDateTime } from "@/shared/format";
import { Button } from "@/shared/ui/button";
import { ErrorNote, LoadingBlock } from "@/shared/ui/states";

const GRAPH_LIMIT = 48;

type Selection = { kind: "node"; key: string } | { kind: "relation"; key: string } | null;
type Detail =
  | { kind: "node"; record: CanonicalNodeDetailRecord }
  | { kind: "relation"; record: CanonicalRelationDetailRecord };

function primaryValue(properties: Record<string, unknown>): string | null {
  for (const key of ["name", "title", "label", "display_name", "hadith_ref", "id"]) {
    const value = properties[key];
    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }
  return null;
}

function nodeKey(node: { node_type: string; merge_key: string }): string {
  return `${node.node_type}::${node.merge_key}`;
}

function nodeLabel(node: { node_type: string; merge_key: string; properties: Record<string, unknown> }): string {
  return primaryValue(node.properties) ?? node.merge_key.slice(0, 12);
}

function relationKey(relation: CanonicalRelationRecord): string {
  return [
    relation.relation_type,
    relation.from_node_type,
    relation.from_merge_key,
    relation.to_node_type,
    relation.to_merge_key,
  ].join("::");
}

/** Developer view: the raw nodes and relations written to the graph, with their sources. */
export function GraphExplorer({ project }: { project: ProjectRecord }) {
  const [snapshot, setSnapshot] = useState<GraphSnapshot | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [nodeType, setNodeType] = useState("");
  const [relationType, setRelationType] = useState("");
  const [reloadToken, setReloadToken] = useState(0);
  const [selection, setSelection] = useState<Selection>(null);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [detailError, setDetailError] = useState<unknown>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    void loadGraphSnapshot(project.project_id, {
      nodeType: nodeType || undefined,
      relationType: relationType || undefined,
      limit: GRAPH_LIMIT,
    })
      .then((result) => {
        if (!cancelled) {
          setSnapshot(result);
        }
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setError(reason);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [project.project_id, nodeType, relationType, reloadToken]);

  useEffect(() => {
    setDetail(null);
    setDetailError(null);
    if (!selection || !snapshot) {
      return;
    }
    let cancelled = false;
    const load = async (): Promise<Detail | null> => {
      if (selection.kind === "node") {
        const node = snapshot.nodes.find((item) => nodeKey(item) === selection.key);
        return node
          ? {
              kind: "node",
              record: await getGraphNodeDetail(project.project_id, node.node_type, node.merge_key),
            }
          : null;
      }
      const relation = snapshot.relations.find(
        (item, index) => `${relationKey(item)}#${index}` === selection.key,
      );
      return relation
        ? {
            kind: "relation",
            record: await getGraphRelationDetail(project.project_id, {
              relationType: relation.relation_type,
              fromNodeType: relation.from_node_type,
              fromMergeKey: relation.from_merge_key,
              toNodeType: relation.to_node_type,
              toMergeKey: relation.to_merge_key,
            }),
          }
        : null;
    };
    void load()
      .then((result) => {
        if (!cancelled) {
          setDetail(result);
        }
      })
      .catch((reason: unknown) => {
        if (!cancelled) {
          setDetailError(reason);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [project.project_id, selection, snapshot]);

  const labelByKey = new Map((snapshot?.nodes ?? []).map((node) => [nodeKey(node), nodeLabel(node)]));
  const relationTypes = Array.from(
    new Set([...(snapshot?.relations ?? []).map((item) => item.relation_type), relationType]),
  )
    .filter(Boolean)
    .sort((left, right) => left.localeCompare(right));

  return (
    <div className="adv-layout">
      <div className="card stack">
        <div className="row-between">
          <h3>Ham graf</h3>
          <Button size="sm" variant="quiet" onClick={() => setReloadToken((token) => token + 1)}>
            Yenile
          </Button>
        </div>
        {error ? (
          <ErrorNote title="Graf okunamadı." error={error} />
        ) : snapshot === null ? (
          <LoadingBlock label="Graf yükleniyor" lines={5} />
        ) : (
          <>
            <p className="muted small num">
              Grafta {snapshot.overview.node_count} düğüm ve {snapshot.overview.relation_count}{" "}
              ilişki var. Her listede en çok {GRAPH_LIMIT} kayıt gösterilir.
            </p>
            <div className="field-grid">
              <label className="field">
                <span>Düğüm türü</span>
                <select value={nodeType} onChange={(event) => setNodeType(event.currentTarget.value)}>
                  <option value="">Hepsi</option>
                  {snapshot.overview.node_type_counts.map((item) => (
                    <option key={item.node_type} value={item.node_type}>
                      {item.node_type} ({item.count})
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>İlişki türü</span>
                <select
                  value={relationType}
                  onChange={(event) => setRelationType(event.currentTarget.value)}
                >
                  <option value="">Hepsi</option>
                  {relationTypes.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <section className="stack-sm">
              <h4>Düğümler</h4>
              {snapshot.nodes.length === 0 ? (
                <p className="muted small">
                  Bu filtreye uyan düğüm yok. Düğümler, bir hadis grafa yazıldığında oluşur.
                </p>
              ) : (
                <ul className="list-rows list-rows-scroll">
                  {snapshot.nodes.map((node: CanonicalNodeRecord) => {
                    const key = nodeKey(node);
                    return (
                      <li key={key}>
                        <button
                          type="button"
                          className={`list-row${selection?.kind === "node" && selection.key === key ? " is-selected" : ""}`}
                          onClick={() => setSelection({ kind: "node", key })}
                        >
                          <strong dir="auto">{nodeLabel(node)}</strong>
                          <span className="muted small">{node.node_type}</span>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
            </section>

            <section className="stack-sm">
              <h4>İlişkiler</h4>
              {snapshot.relations.length === 0 ? (
                <p className="muted small">
                  Bu filtreye uyan ilişki yok. İlişkiler, bir hadis grafa yazıldığında oluşur.
                </p>
              ) : (
                <ul className="list-rows list-rows-scroll">
                  {snapshot.relations.map((relation, index) => {
                    // Several links can join the same two nodes, so the position is part of the key.
                    const key = `${relationKey(relation)}#${index}`;
                    const from =
                      labelByKey.get(`${relation.from_node_type}::${relation.from_merge_key}`) ??
                      relation.from_merge_key.slice(0, 12);
                    const to =
                      labelByKey.get(`${relation.to_node_type}::${relation.to_merge_key}`) ??
                      relation.to_merge_key.slice(0, 12);
                    return (
                      <li key={key}>
                        <button
                          type="button"
                          className={`list-row${selection?.kind === "relation" && selection.key === key ? " is-selected" : ""}`}
                          onClick={() => setSelection({ kind: "relation", key })}
                        >
                          <strong>{relation.relation_type}</strong>
                          <span className="muted small" dir="auto">
                            {from} → {to}
                          </span>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
            </section>
          </>
        )}
      </div>

      <div className="card stack">
        {detailError ? (
          <ErrorNote title="Kaydın ayrıntısı okunamadı." error={detailError} />
        ) : !selection ? (
          <p className="muted">
            Soldan bir düğüm ya da ilişki seçtiğinde alanları, geldiği kaynak birimleri ve
            dayandığı metin parçaları burada görünür.
          </p>
        ) : !detail ? (
          <LoadingBlock label="Kayıt yükleniyor" lines={5} />
        ) : detail.kind === "node" ? (
          <>
            <div className="row-between">
              <h3 dir="auto">{nodeLabel(detail.record.node)}</h3>
              <span className="tag">{detail.record.node.node_type}</span>
            </div>
            <dl className="def-grid">
              <div>
                <dt>Kimlik anahtarı</dt>
                <dd>{detail.record.node.merge_key}</dd>
              </div>
              <div>
                <dt>Son run</dt>
                <dd>{detail.record.node.last_run_id ?? "kayıt yok"}</dd>
              </div>
              <div>
                <dt>Güncellendi</dt>
                <dd>{formatDateTime(detail.record.node.updated_at)}</dd>
              </div>
            </dl>
            <section className="stack-sm">
              <h4>Alanlar</h4>
              <pre className="json-block" dir="auto">
                {JSON.stringify(detail.record.node.properties, null, 2)}
              </pre>
            </section>
            <Sources units={detail.record.source_units} segments={detail.record.supporting_segments} />
            <section className="stack-sm">
              <h4>Bağlı ilişkiler ({detail.record.connected_relations.length})</h4>
              {detail.record.connected_relations.length === 0 ? (
                <p className="muted small">Bu düğüme bağlı ilişki yok.</p>
              ) : (
                <ul className="list-rows list-rows-scroll">
                  {detail.record.connected_relations.map((relation, index) => (
                    <li key={index} className="list-row">
                      <strong>
                        {relation.relation_type} · {relation.direction === "incoming" ? "gelen" : "giden"}
                      </strong>
                      <span className="muted small" dir="auto">
                        {relation.other_node_type} ·{" "}
                        {primaryValue(relation.other_node_properties) ??
                          relation.other_merge_key.slice(0, 12)}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </>
        ) : (
          <>
            <div className="row-between">
              <h3>{detail.record.relation.relation_type}</h3>
              <span className="tag">ilişki</span>
            </div>
            <dl className="def-grid">
              <div>
                <dt>Kaynak düğüm</dt>
                <dd dir="auto">{nodeLabel(detail.record.from_node)}</dd>
              </div>
              <div>
                <dt>Hedef düğüm</dt>
                <dd dir="auto">{nodeLabel(detail.record.to_node)}</dd>
              </div>
              <div>
                <dt>Son run</dt>
                <dd>{detail.record.relation.last_run_id ?? "kayıt yok"}</dd>
              </div>
              <div>
                <dt>Güncellendi</dt>
                <dd>{formatDateTime(detail.record.relation.updated_at)}</dd>
              </div>
            </dl>
            <section className="stack-sm">
              <h4>Alanlar</h4>
              <pre className="json-block" dir="auto">
                {JSON.stringify(detail.record.relation.properties, null, 2)}
              </pre>
            </section>
            <Sources units={detail.record.source_units} segments={detail.record.supporting_segments} />
          </>
        )}
      </div>
    </div>
  );
}

function Sources({
  units,
  segments,
}: {
  units: CanonicalSourceUnitRefRecord[];
  segments: CanonicalSegmentSupportRecord[];
}) {
  return (
    <>
      <section className="stack-sm">
        <h4>Kaynak birimleri ({units.length})</h4>
        {units.length === 0 ? (
          <p className="muted small">Bu kayıt için kaynak birimi saklanmamış.</p>
        ) : (
          <ul className="row">
            {units.map((unit) => (
              <li key={unit.source_unit_id} className="tag">
                {unit.title ?? unit.source_unit_id}
              </li>
            ))}
          </ul>
        )}
      </section>
      <section className="stack-sm">
        <h4>Dayandığı segmentler ({segments.length})</h4>
        {segments.length === 0 ? (
          <p className="muted small">Bu kayıt için segment saklanmamış.</p>
        ) : (
          <ul className="list-rows list-rows-scroll">
            {segments.map((segment) => (
              <li key={segment.segment_id} className="list-row">
                <span className="muted small">Segment {segment.segment_order ?? "?"}</span>
                <span dir="auto">{segment.text}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
