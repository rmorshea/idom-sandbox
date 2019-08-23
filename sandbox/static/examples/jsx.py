import idom

module = idom.Module("""
function Button({onClick}) {
    return (
    	<button onClick={onClick}>
        	Click Me!
        </button>
    );
}

return {
    Button: Button
};
""")


async def click(event):
    print("CLICK EVENT")
    for k, v in event.items():
        print(" ", k, ":", v)


module.Button(onClick=click)
