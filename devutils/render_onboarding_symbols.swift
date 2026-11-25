// Copyright 2026 The Lune Authors
// Use of this source code is governed by the GPL-3.0 license in LICENSE.

import AppKit

enum RenderError: Error {
    case missingSymbol(String)
    case couldNotEncode(String)
}

guard CommandLine.arguments.count == 2 else {
    fputs("Usage: render_onboarding_symbols.swift OUTPUT_DIRECTORY\n", stderr)
    exit(2)
}
let destination = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
try FileManager.default.createDirectory(at: destination, withIntermediateDirectories: true)
let symbols = [
    "point.3.connected.trianglepath.dotted",
    "eye.slash",
    "magnifyingglass",
    "square.and.arrow.down",
    "lock.badge.checkmark",
    "paintbrush.pointed",
]
let pixels = 96
let canvas = CGFloat(pixels)
let appearance = NSAppearance(named: .aqua)!
let config = NSImage.SymbolConfiguration(pointSize: 75, weight: .medium)
    .applying(.preferringMonochrome())

for symbol in symbols {
    var configuredImage: NSImage?
    appearance.performAsCurrentDrawingAppearance {
        configuredImage = NSImage(systemSymbolName: symbol, accessibilityDescription: nil)?
            .withSymbolConfiguration(config)
    }
    guard let image = configuredImage else {
        throw RenderError.missingSymbol(symbol)
    }
    guard let bitmap = NSBitmapImageRep(
        bitmapDataPlanes: nil, pixelsWide: pixels, pixelsHigh: pixels,
        bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0, bitsPerPixel: 0
    ), let context = NSGraphicsContext(bitmapImageRep: bitmap) else {
        throw RenderError.couldNotEncode(symbol)
    }
    let scale = min(1, (canvas - 6) / max(image.size.width, image.size.height))
    let width = image.size.width * scale
    let height = image.size.height * scale
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = context
    context.cgContext.clear(CGRect(x: 0, y: 0, width: canvas, height: canvas))
    appearance.performAsCurrentDrawingAppearance {
        image.draw(in: CGRect(
            x: (canvas - width) / 2, y: (canvas - height) / 2,
            width: width, height: height
        ))
    }
    NSGraphicsContext.restoreGraphicsState()
    guard let data = bitmap.representation(using: .png, properties: [:]) else {
        throw RenderError.couldNotEncode(symbol)
    }
    try data.write(to: destination.appendingPathComponent(symbol + ".png"), options: .atomic)
    print(symbol)
}
