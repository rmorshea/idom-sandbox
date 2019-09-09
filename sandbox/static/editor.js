Promise.all([
    import('https://dev.jspm.io/react-codemirror2'),
    import('https://dev.jspm.io/codemirror/mode/python/python')
]).then(pkgs => {
    const CodeMirror = pkgs[0].default.UnControlled;
    return {
        Editor: function Show({ value, options, onChange }) {
            function handleChange(editor, data, value) {
                if (onChange) {
                    onChange(value);
                }
            }
            return (
                <CodeMirror
                    value={value}
                    options={options}
                    onChange={handleChange}
                />
            );
        }
    }
})
