# EVY LLM And RAG Tuning

EVY does not need model training before first hardware. It needs repeatable evaluation of retrieval quality, prompt style, and SMS-sized answers.

Status: pre-hardware retrieval tuning is implemented with a sample knowledge pack and evaluation cases. Real LLM prompt scoring waits until the BitNet service is installed and reachable.

## What Is Tested Now

Script:

- `scripts/tune_llm_rag_prompts.py`

Default inputs:

- sample pack: `examples/knowledge_packs/evy_local_emergency_sample/`
- evaluation cases: `examples/evaluation/llm_rag_tuning_cases.json`
- report: `data/lilevy/software_reports/llm_rag_tuning_report.json`

The harness checks:

- knowledge-pack import into SQLite RAG
- retrieval query per case
- expected terms in retrieved context
- whether a real LLM service is reachable
- prompt template responses when the service exists
- SMS length
- required response terms
- forbidden response phrases

## Run Retrieval Tuning Without LLM

This is useful right now on any development machine:

```bash
python scripts/tune_llm_rag_prompts.py --llm-url http://127.0.0.1:1
```

Expected result before BitNet is running:

- retrieval passes
- `llm_health.available` is false
- prompt results are empty
- overall report passes because `--require-llm` was not set

## Run Full Prompt Tuning With BitNet

After the BitNet service is running:

```bash
python scripts/tune_llm_rag_prompts.py \
  --llm-url http://127.0.0.1:18002 \
  --require-llm
```

This should be run after:

```bash
python scripts/validate_bitnet_local_llm.py --health-url http://127.0.0.1:18002/health
python scripts/benchmark_bitnet_sms_prompts.py --base-url http://127.0.0.1:18002
```

## Why Not Train Yet

Use RAG for facts because local emergency facts expire and need source tracking. Use prompt tuning for style and SMS length. Use rules/templates for critical safety behavior.

Fine-tuning should wait until:

- BitNet is measured on Raspberry Pi hardware
- retrieval failures are understood
- prompt failures repeat across multiple runs
- the team has approved response examples
- privacy rules are clear

If fine-tuning is ever needed, use synthetic and approved examples, not private SMS logs.

## Current Evaluation Cases

The default cases cover:

- storm shelter guidance
- boil-water guidance
- Plus Code handling
- generator/carbon monoxide safety
- medication cold storage during outage
- heat exhaustion
- downed power lines

Add new cases by editing:

- `examples/evaluation/llm_rag_tuning_cases.json`

Each case can define:

- `query`
- `retrieval_query`
- `category`
- `expected_terms`
- `response_should_include`
- `response_should_avoid`
- `response_max_chars`

## Validation

```bash
python -m pytest backend/tests/test_llm_rag_tuning_script.py -q
python scripts/tune_llm_rag_prompts.py --llm-url http://127.0.0.1:1
```

## Remaining Work

- Run `--require-llm` against real BitNet.
- Add more local/community cases once official sources are chosen.
- Compare prompt templates by latency, SMS length, and safety scoring.
- Feed failures back into prompt templates and retrieval query rules before considering fine-tuning.
