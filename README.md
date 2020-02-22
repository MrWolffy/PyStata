# PyStata

A naive Stata interpreter in Python

Notice:

- This project is NOT for commercial use.
- The author is NOT responsible for any consequences caused by using this project.

## Syntax supported

- `in`

## Command supported

- `describe`
- `exit`
- `pwcorr`
- `regress`
- `sysuse`

---

## To begin

To create a Stata platform:

```
platform = StataPlatform()
```

To run the platform:

```
platform.run()
```

You can use `sysuse auto` to import a demo dataset.
