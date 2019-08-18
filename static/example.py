# ------- IDOM SANDBOX -----------
# TRY EDITING THE CODE AND PLAYING
# WITH THE INTERACTIVE VIEW TO THE
# RIGHT ------------------------}>

import idom

@idom.element
async def Slideshow(self, index=0):

    async def update_image(event):
        self.update(index + 1)
        print("CLICK EVENT")
        for k, v in event.items():
            print(" ", k, ":", v)

    return idom.html.img(
        src=f"https://picsum.photos/500/300?image={index}",
        onClick=update_image,
    )

print("Click the image 🖱️", "\n")

Slideshow()
