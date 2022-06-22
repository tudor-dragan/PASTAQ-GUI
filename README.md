This is a simple GUI that can be used to setup the parametrization of
[PASTAQ's][pastaq]
Data Dependent Acquisition (DDA) pipeline. To run this program, install `PyQT5`, `pastaq` and `pyrcc5` with `pip`, generate the resources with the `pyrcc5 src/resources.qrc -0 src/resources.py` command and run the `src/app.py` file.

```
pip install pastaq PyQt5 pyrcc5
pyrcc5 src/resources.qrc -0 src/resources.py
python src/app.py
```

Alternatively, you can find Windows executable files on the release page. These
were created with `pyinstaller` and don't require installation.

Please keep in mind that this software in early development, and unexpected
errors can appear. When/if that happens, feel free to report an issue with steps
to reproduce the problem and if possible the files used when the error appeared.

A brief tutorial of the usage of PASTAQ-GUI can be found on the [official PASTAQ
website][gui-tutorial].

[pastaq]: https://github.com/PASTAQ-MS/PASTAQ
[gui-tutorial]: https://pastaq.horvatovichlab.com/gui-tutorial/index.html
