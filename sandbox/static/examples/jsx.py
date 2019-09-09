import idom

Button = idom.Eval("""
({onClick}) => {
    return (
    	<button onClick={onClick}>
        	Click Me!
        </button>
    );
}
""")


async def click(event):
    print("CLICK EVENT")
    for k, v in event.items():
        print(" ", k, ":", v)


Button(onClick=click)
