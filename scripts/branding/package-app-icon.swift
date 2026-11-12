// Fit Apple's full-bleed rendition into its compiled legacy macOS canvas.
// Use actool's native size-specific margins, with a clean transparent canvas.
import AppKit
let args = CommandLine.arguments
let native = NSBitmapImageRep(data: try Data(contentsOf: URL(fileURLWithPath: args[1])))!
let artwork = NSImage(contentsOfFile: args[2])!
let size = native.pixelsWide
let middle = size / 2
// Mid-alpha follows the native tile edge without including its outer shadow.
let opaque = (0..<size).filter { native.colorAt(x: $0, y: middle)!.alphaComponent >= 0.5 }
let inset = opaque.first!
let extent = opaque.last! + 1 - inset
let result = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: size, pixelsHigh: size,
    bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
    colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: result)
NSGraphicsContext.current!.imageInterpolation = .high
// Do not carry over the older renderer's rim or shadow: its pixels can leave
// straight seams around the new mask. Icon Composer renders all artwork effects.
artwork.draw(in: NSRect(x: inset, y: inset, width: extent, height: extent),
    from: .zero, operation: .sourceOver, fraction: 1)
NSGraphicsContext.restoreGraphicsState()
try result.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: args[1]))
