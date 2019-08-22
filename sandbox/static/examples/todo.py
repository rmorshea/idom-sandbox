import idom


@idom.element
async def Todo(self):
    items = []

    async def add_new_task(event):
        if event["key"] == "Enter":
            items.append(event["value"])
            task_list.update(items)

    task_input = idom.html.input(onKeyDown=add_new_task)
    task_list = TaskList(items)

    return idom.html.div(task_input, task_list)


@idom.element
async def TaskList(self, items):
    tasks = []

    for index, text in enumerate(items):

        async def remove(event, index=index):
            del items[index]
            self.update(items)

        task_text = idom.html.td(idom.html.p(text))
        delete_button = idom.html.td(idom.html.button("x"), onClick=remove)
        tasks.append(idom.html.tr(task_text, delete_button, style={"color": "white"}))

    return idom.node("table", tasks)


print("Try typing in the text box and pressing 'Enter' 📋")

Todo()
