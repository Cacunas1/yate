---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Mojo
    language: mojo
    name: mojo-jupyter-kernel
---

# Sandbox: Testing code using a Jupyter notebook

```mojo
var filename = "dummy.txt"

var text: String

text = "test dummy text"

with open(filename, "w") as file:
    file.write(text)

with open(filename, "r") as file:
    text = file.read()

print(text)

```
