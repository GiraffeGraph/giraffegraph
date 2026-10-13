# A Human-in-the-Loop Knowledge Graph Generation Engine for Preventing Hallucination and Schema Drift in LLMs: An Application on Hadith Isnad Chains

**Senior Design Project Report**

Yahya Efe Kuruçay, Deniz Büyükşahin, Alperen Ulukaya

Supervisor: Dr. Taha Yiğit Alkan

Akdeniz University, Faculty of Engineering, Department of Computer Engineering

CSE 491 Senior Design Project I, Fall 2026–2027

Draft of 13 October 2026

# Abstract

Large language models can turn text into knowledge graph facts, but they add facts the source does not contain and they drift from the schema they were given. This report presents GiraffeGraph Core, an engine in which the model only proposes. Each proposed fact carries a quotation from the source, deterministic checks decide whether a person must look at it, and a fact reaches the graph only with a recorded acceptance, either a reviewer's decision or a named automatic policy. The case study is the isnad, the chain of narrators that precedes a hadith. The design rests on one claim: what a knowledge layer built with a language model has to store is the decision of a person, and what can be derived from the source is derived again.

We evaluate the engine on 300 hadiths from the six canonical collections, using the narrator labels of an existing platform-derived corpus as reference, with a fixed matching protocol and hadith-level bootstrap intervals. Under loose matching a rule-based parser reaches F1 0.923, a model constrained only by the schema 0.890, and the same model with type descriptions and domain hints 0.956; under strict matching both model conditions are above the parser. A check that the extracted name occurs inside the model's own quotation flags 9% of the schema-only model's proposals. Of the flagged proposals 79% do not match the reference, and they are 84% of all its unmatched proposals; most are names the model transliterated, put in another grammatical case or inferred from a kinship reference. Candidates accepted without review rise from precision 0.914 to 0.985. A check that the quotation occurs in the source finds nothing, because the model quotes correctly and changes the name. The model's self-reported confidence separates matched from unmatched proposals poorly (AUC 0.634). Identifying a narrator by the written name places one chain position in ten under a name shared by several people.

Two supporting studies test the storage side of the claim. In a simulation on 27,056 labelled chains, an identity decision keyed by the written name alone is reused wrongly for one mention in ten; deriving the scope of a decision from contradictions that a deterministic rule detects brings the silent error to 0.014 per mention with about half the reviewer questions that a fixed narrow key needs, and the result repeats on a second label set and on held-out collections. In a second domain, a coding agent answers questions about why the engine's code is the way it is 0% to 4% correctly from the code alone and 88% to 100% correctly with a ledger of decisions, while it reads structural facts from the code without any documentation when it has enough tool calls.

The reference labels are not a human gold standard, no person reviewed the runs, one model produced usable results in the engine evaluation, the reviewer in the ledger study is simulated from labels, and the experiments ran on the engine's in-memory backend. The software has 285 automated backend tests, twelve of which exercise the pipeline on PostgreSQL and Neo4j, and includes a dashboard in which a chain can be read with the source quotation and the acceptance record of every link.

**Keywords:** knowledge graph, large language models, human-in-the-loop, grounding, decision record, schema drift, hadith, isnad
