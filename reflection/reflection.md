# Reflection

## Pipeline Differences

The manual pipeline was the most deliberate and evidence-driven because the review groups, personas, requirements, and tests were all created by reading the cleaned reviews directly. The automated pipeline was the fastest, but it produced more abstract personas and more vague requirements, especially in the specification stage. The hybrid pipeline started from the automated artifacts and improved them by removing unsupported assumptions, tightening group themes, and rewriting requirements so they were easier to trace and test.

## Clearest Personas

The clearest personas came from the **manual** pipeline. They were narrower, more directly supported by review evidence, and better aligned with specific user situations. The automated personas were usable, but several descriptions generalized beyond what the grouped reviews clearly supported. The hybrid personas became more precise after revision, but they still began from the broader automated framing.

## Most Useful Requirements

The most useful requirements came from the **hybrid** pipeline. The manual requirements were already specific, but the hybrid requirements benefited from starting with automated coverage and then being rewritten to improve clarity, scope, and testability. The automated requirements were the weakest because they often used broader or less measurable language.

## Strongest Traceability

The strongest traceability was shared by the **manual** and **hybrid** pipelines. Both kept explicit links from review groups to personas and from personas to requirements and tests. The automated pipeline also preserved formal traceability fields, but the quality of those links was weaker because some generated requirements and persona statements were less grounded in the review evidence.

## Problems in the Automated Outputs

The main issues in the automated outputs were vague wording, unsupported assumptions, and over-generalization. Some automated personas added claims that were not strongly supported by the grouped reviews. Some automated requirements were grammatically correct but too broad to support strong validation tests. The automated pipeline was useful for speed and coverage, but it still needed human revision to improve precision and reduce ambiguity.
