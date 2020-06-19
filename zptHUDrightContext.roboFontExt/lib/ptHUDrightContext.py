from AppKit import NSImage, NSAffineTransform, NSBezierPath,\
    NSLeftTextAlignment, NSRightTextAlignment, NSCenterTextAlignment,\
    NSFocusRingTypeNone, NSColor, NSViewMaxXMargin
import vanilla
from mojo import events
from roboHUD import RoboHUDController, BaseRoboHUDControl, registerControlClass
from mojo.events import addObserver
from mojo.drawingTools import save, restore, translate
from lib.tools.drawing import strokePixelPath
from mojo.UI import UpdateCurrentGlyphView, CurrentGlyphWindow
from defconAppKit.tools.textSplitter import splitText

# import ptHUDglyphUnicode


class ptHUDrightContext(BaseRoboHUDControl):

    name = "PT Right Context"
    size = (300, 30)

    def start(self):
        self.rightInput = "n"

        super(ptHUDrightContext, self).start()

        addObserver(self, "drawNeighbors", "drawBackground")
        addObserver(self, "drawPreviewNeighBors", "drawPreview")
        addObserver(self, "currentFontChanged", "fontBecameCurrent")


        foregroundColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.0, 0.0, 0.0, 0.7)
        backgroundColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.0, 0.0, 0.0, 0.05)


        self.view.unicodeRightEditText = vanilla.EditText(
            (255, 0, 40, 19),
            "n",
            callback=self.editRightCallback,
            continuous=False,
            sizeStyle="small"
        )


        controls = [
            (self.view.unicodeRightEditText, NSCenterTextAlignment),
        ]
        for control, alignment in controls:
            textField = control.getNSTextField()
            textField.setBordered_(False)
            textField.setTextColor_(foregroundColor)
            textField.setBackgroundColor_(backgroundColor)
            textField.setFocusRingType_(NSFocusRingTypeNone)
            textField.setAlignment_(alignment)


    def stop(self):
        super(ptHUDrightContext, self).stop()
        events.removeObserver(self, "fontBecameCurrent")
        events.removeObserver(self, "drawBackground")
        events.removeObserver(self, "drawPreview")



    def currentFontChanged(self, notification):
        self.view.unicodeRightEditText.set("")
        
    def editRightCallback(self, sender):
        self.rightInput = sender.get()

    def stringToGlyphs(self, text, font):
        glyphRecord = []
        cmap = font.getCharacterMapping()
        if isinstance(text, str):
            text = text
        lines = text.split('\n')
        for line in lines:    
            glyphRecord += splitText(line, cmap)
            glyphRecord.append('\n')
        glyphRecord.pop()     
        return glyphRecord

    def drawPreviewNeighBors(self, info):
        save()
        self._drawRightNeighborsGlyphs(info["glyph"], scale=1, stroke=False)
        UpdateCurrentGlyphView()
        restore()

    def drawNeighbors(self, info):
        save()
        fillColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.0, 0.0, 0.0, 0.05)
        fillColor.set()
        self._drawRightNeighborsGlyphs(info["glyph"], scale=1, stroke=False)
        UpdateCurrentGlyphView()
        restore()

    
    def _drawRightNeighborsGlyphs(self, glyph, stroke=True, scale=1):
        if glyph is None:
            return
        font = glyph.font

        # left = self.view.unicodeLeftEditText.get()
        right = self.view.unicodeRightEditText.get()
        # right = self.rightInput
        right = self.stringToGlyphs(right, font)

        save()

        

        for index, rightGlyph in enumerate(list(right)):
            if rightGlyph in font:
                rightGlyph = font[rightGlyph]
                
                # translate back the width of the glyph
                if index == 0:
                    translate(glyph.width, 0)
                else:
                    translate(font[list(right)[index-1]].width, 0)
                # performance tricks, the naked attr will return the defcon object
                # and get the cached bezier path to draw
                path = rightGlyph.naked().getRepresentation("defconAppKit.NSBezierPath")
                # fill the path
                path.fill()
                if stroke:
                    path.setLineWidth_(scale)
                    strokePixelPath(path)
        restore()


registerControlClass(ptHUDrightContext)

