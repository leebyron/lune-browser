// Rasterize the shared Lune geometry and light/dark palettes with AppKit.
import AppKit
let output = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "out/branding"
let data = try Data(contentsOf: URL(fileURLWithPath: "branding/palettes.json"))
let config = try JSONSerialization.jsonObject(with: data) as! [String: Any]
let geometry = config["geometry"] as! [String: Double]
let radius = geometry["outer_radius"]!
let offset = geometry["center_offset"]!
let halfHeight = sqrt(radius * radius - offset * offset)
let innerReach = radius + offset - 2 * offset * geometry["width_multiplier"]!
let innerRadius = (innerReach * innerReach + halfHeight * halfHeight) / (2 * innerReach)
let innerOffset = innerRadius - innerReach
func ink(_ mode: String, _ name: String) -> UInt32 {
    let palette = config[mode] as! [String: String]
    return UInt32(palette[name]!.dropFirst(), radix: 16)!
}
let fm = FileManager.default
func color(_ hex: UInt32) -> NSColor {
    NSColor(srgbRed: CGFloat((hex >> 16) & 255) / 255,
            green: CGFloat((hex >> 8) & 255) / 255,
            blue: CGFloat(hex & 255) / 255, alpha: 1)
}
func render(_ size: Int, _ file: String, mono: Bool = false, wordmark: Bool = false, white: Bool = false, mode: String = "dark", opaque: Bool = false) throws {
    let width = wordmark ? size * 140 / 32 : size
    let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: width, pixelsHigh: size,
        bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
        colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
    let context = NSGraphicsContext(bitmapImageRep: rep)!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = context
    let cg = context.cgContext
    cg.scaleBy(x: CGFloat(size) / 1024, y: CGFloat(size) / 1024)
    cg.saveGState()
    if opaque {
        color(ink(mode, "ground")).setFill()
        NSRect(x: 0, y: 0, width: 1024, height: 1024).fill()
    }
    if !mono {
        color(ink(mode, "ground")).setFill()
        NSBezierPath(roundedRect: NSRect(x: 64, y: 64, width: 896, height: 896), xRadius: 200, yRadius: 200).fill()
    }
    cg.translateBy(x: 152, y: 152); cg.scaleBy(x: 2.4, y: 2.4)
    for (center, cutout, ink) in [(150-offset, 150+innerOffset, ink(mode, "left")), (150+offset, 150-innerOffset, ink(mode, "right"))] {
        cg.saveGState()
        cg.addRect(CGRect(x: 0, y: 0, width: 300, height: 300))
        cg.addEllipse(in: CGRect(x: cutout - innerRadius, y: 150-innerRadius, width: 2*innerRadius, height: 2*innerRadius))
        cg.clip(using: .evenOdd)
        color(mono ? (white ? 0xFFFFFF : 0x000000) : ink).setFill()
        NSBezierPath(ovalIn: NSRect(x: center - radius, y: 150-radius, width: 2*radius, height: 2*radius)).fill()
        cg.restoreGState()
    }
    cg.restoreGState()
    if wordmark {
        let attrs: [NSAttributedString.Key: Any] = [
            .font: NSFont.systemFont(ofSize: 768, weight: .medium),
            .foregroundColor: color(ink(mode, "text")),
        ]
        ("Lune" as NSString).draw(at: NSPoint(x: 1152, y: 48), withAttributes: attrs)
    }
    NSGraphicsContext.restoreGraphicsState()
    try rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: file))
}
for mode in ["light", "dark"] {
    let iconset = output + "/Lune-" + mode + ".iconset"
    try fm.createDirectory(atPath: iconset, withIntermediateDirectories: true)
    for size in [16, 32, 128, 256, 512] {
        try render(size, iconset + "/icon_\(size)x\(size).png", mode: mode)
        try render(size * 2, iconset + "/icon_\(size)x\(size)@2x.png", mode: mode)
    }
    try render(1024, output + "/lune-" + mode + ".png", mode: mode)
}
try fm.createDirectory(atPath: output + "/internal", withIntermediateDirectories: true)
for size in [16, 24, 32, 48, 64, 128, 256] {
    try render(size, output + "/internal/product_logo_\(size).png")
}
try render(22, output + "/internal/product_logo_22_mono.png", mono: true)
for (size, suffix) in [(32, ""), (64, "_200")] {
    try render(size, output + "/internal/product_logo\(suffix).png", wordmark: true, mode: "light")
    try render(size, output + "/internal/product_logo_white\(suffix).png", wordmark: true, mode: "dark")
}
try render(180, output + "/apple-touch-icon.png", opaque: true)
