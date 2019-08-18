import idom

@idom.element
async def Slideshow(self, index=0):

    async def update_image(event):
        self.update(index + 1)
        print(event)

    return idom.html.img(
        src=f"https://picsum.photos/500/300?image={index}",
        onClick=update_image,
    )

print("Try clicking the image! 🖱️")

Slideshow()
