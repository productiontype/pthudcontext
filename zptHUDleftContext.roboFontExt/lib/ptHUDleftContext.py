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


class ptHUDleftContext(BaseRoboHUDControl):

    name = "PT Left Context"
    size = (300, 30)

    def start(self):
        self.leftInput = "n"

        super(ptHUDleftContext, self).start()

        addObserver(self, "drawNeighbors", "drawBackground")
        addObserver(self, "drawPreviewNeighBors", "drawPreview")
        addObserver(self, "currentFontChanged", "fontBecameCurrent")


        foregroundColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.0, 0.0, 0.0, 0.7)
        backgroundColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.0, 0.0, 0.0, 0.05)


        self.view.unicodeLeftEditText = vanilla.EditText(
            (0, 0, 40, 19),
            "n",
            callback=self.editLeftCallback,
            continuous=False,
            sizeStyle="small"
        )

        controls = [
            (self.view.unicodeLeftEditText, NSCenterTextAlignment),
        ]
        for control, alignment in controls:
            textField = control.getNSTextField()
            textField.setBordered_(False)
            textField.setTextColor_(foregroundColor)
            textField.setBackgroundColor_(backgroundColor)
            textField.setFocusRingType_(NSFocusRingTypeNone)
            textField.setAlignment_(alignment)



    def stop(self):
        super(ptHUDleftContext, self).stop()
        events.removeObserver(self, "fontBecameCurrent")
        events.removeObserver(self, "drawBackground")
        events.removeObserver(self, "drawPreview")



    def currentFontChanged(self, notification):
        self.view.unicodeLeftEditText.set("")

    def editLeftCallback(self, sender):
        self.leftInput = sender.get()
        
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
        self._drawLeftNeighborsGlyphs(info["glyph"], scale=1, stroke=False)
        UpdateCurrentGlyphView()
        restore()

    def drawNeighbors(self, info):
        save()
        fillColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.0, 0.0, 0.0, 0.05)
        fillColor.set()
        self._drawLeftNeighborsGlyphs(info["glyph"], scale=info["scale"])
        UpdateCurrentGlyphView()
        restore()

    def _drawLeftNeighborsGlyphs(self, glyph, stroke=True, scale=1):
        if glyph is None:
            return
        font = glyph.font

        left = self.view.unicodeLeftEditText.get()
        left = self.stringToGlyphs(left, font)
        
        save()
        for index, leftGlyph in enumerate(reversed(list(left))):
            if leftGlyph in font:
                
                leftGlyph = font[leftGlyph]
                
                # translate back the width of the glyph
                translate(-leftGlyph.width, 0)
                # performance tricks, the naked attr will return the defcon object
                # and get the cached bezier path to draw
                path = leftGlyph.naked().getRepresentation("defconAppKit.NSBezierPath")
                # fill the path
                path.fill()
                if stroke:
                    path.setLineWidth_(scale)
                    strokePixelPath(path)
        restore()


registerControlClass(ptHUDleftContext)

