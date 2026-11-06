// Reproduce branding/lune.svg as sRGB PNGs and a macOS iconset, using AppKit.
import AppKit
let output = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "out/branding"
let fm = FileManager.default
try fm.createDirectory(atPath: output + "/Lune.iconset", withIntermediateDirectories: true)
func color(_ hex: UInt32) -> NSColor {
    NSColor(srgbRed: CGFloat((hex >> 16) & 255) / 255,
            green: CGFloat((hex >> 8) & 255) / 255,
            blue: CGFloat(hex & 255) / 255, alpha: 1)
}
func render(_ size: Int, _ file: String) throws {
    let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: size, pixelsHigh: size,
        bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
        colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
    let context = NSGraphicsContext(bitmapImageRep: rep)!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = context
    let cg = context.cgContext
    cg.scaleBy(x: CGFloat(size) / 1024, y: CGFloat(size) / 1024)
    color(0x10354F).setFill()
    NSBezierPath(roundedRect: NSRect(x: 64, y: 64, width: 896, height: 896), xRadius: 200, yRadius: 200).fill()
    cg.translateBy(x: 152, y: 152); cg.scaleBy(x: 2.4, y: 2.4)
    for (center, cutout, ink) in [(136.0, 164.0, UInt32(0x00A7BE)), (164.0, 136.0, UInt32(0x5386BF))] {
        cg.saveGState()
        cg.addRect(CGRect(x: 0, y: 0, width: 300, height: 300))
        cg.addEllipse(in: CGRect(x: cutout - 111, y: 39, width: 222, height: 222))
        cg.clip(using: .evenOdd)
        color(ink).setFill()
        NSBezierPath(ovalIn: NSRect(x: center - 111, y: 39, width: 222, height: 222)).fill()
        cg.restoreGState()
    }
    NSGraphicsContext.restoreGraphicsState()
    try rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: file))
}
for size in [16, 32, 128, 256, 512] {
    try render(size, output + "/Lune.iconset/icon_\(size)x\(size).png")
    try render(size * 2, output + "/Lune.iconset/icon_\(size)x\(size)@2x.png")
}
try render(1024, output + "/lune.png")
