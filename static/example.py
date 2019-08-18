import idom

@idom.element
async def Slideshow(self, index=0):

    async def update_image(event):
        self.update(index + 1)
        print("\nCLICK EVENT")
        for k, v in event.items():
            print(" ", k, ":", v)

    return idom.html.img(
        src=f"https://picsum.photos/500/300?image={index}",
        onClick=update_image,
    )

print("Click the image 🖱️")
print("And edit the code 📝")

Slideshow()
