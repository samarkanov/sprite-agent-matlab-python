Source code for the blog entry: https://samarkanov.info/blog/2026/jan/sprite-agent-matlab-python.html

I’m turning a Gemini agent into an industrial health monitor. By nesting the agent in a [sprites.dev](https://sprites.dev/) sandbox, I’ve got it orchestrating a hand-off between MATLAB (for synthetic data generation) and Python (for health analysis) - all while keeping things efficient by passing file paths instead of bulky data chunks. If you've ever wondered how to make LLMs working with MATLAB, Python, Hadoop and Parquet this workflow is for you.

![](https://samarkanov.info/assets/blog-jan-2026/diagram-jan-21.svg)
