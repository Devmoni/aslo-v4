export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"
export PATH="${APPDIR}/usr/bin:${PATH}"

{{ python-executable }} ${APPDIR}/usr/bin/sugarstore_generator "$@"
