import AppKit
import CoreGraphics
import Foundation

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data((message + "\n").utf8))
    exit(1)
}

let args = CommandLine.arguments
guard args.count >= 4, let pid = Int32(args[1]),
      let offsetX = Double(args[2]), let offsetY = Double(args[3]),
      let app = NSRunningApplication(processIdentifier: pid),
      let source = CGEventSource(stateID: .hidSystemState),
      CGPreflightPostEventAccess() else {
    fail("Native gesture requires a running isolated browser and permission to post mouse events.")
}
_ = app.activate(options: [])
Thread.sleep(forTimeInterval: 0.15)
guard NSWorkspace.shared.frontmostApplication?.processIdentifier == pid else {
    fail("Fixture window is inactive.")
}

func windows() -> [[String: Any]] {
    (CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements],
                               kCGNullWindowID) as? [[String: Any]]) ?? []
}
func frame(_ window: [String: Any]) -> CGRect? {
    guard let bounds = window[kCGWindowBounds as String] as? NSDictionary else { return nil }
    return CGRect(dictionaryRepresentation: bounds)
}
let candidates = windows().filter {
    ($0[kCGWindowOwnerPID as String] as? Int32) == pid &&
    ($0[kCGWindowLayer as String] as? Int) == 0
}
func area(_ window: [String: Any]) -> CGFloat {
    guard let bounds = frame(window) else { return 0 }
    return bounds.width * bounds.height
}
// The floating toolbar and traffic-light controls can also be layer zero.
guard let window = candidates.max(by: { area($0) < area($1) }),
      let before = frame(window), let id = window[kCGWindowNumber as String] as? Int else {
    fail("Cannot resolve the fixture's native window.")
}
let start = CGPoint(x: before.minX + offsetX, y: before.minY + offsetY)

var last = CGEvent(source: nil)?.location ?? start
func send(_ type: CGEventType, _ point: CGPoint) {
    guard let event = CGEvent(mouseEventSource: source, mouseType: type,
                              mouseCursorPosition: point, mouseButton: .left) else {
        fail("Cannot create native mouse event.")
    }
    event.setIntegerValueField(.mouseEventClickState, value: 1)
    event.setIntegerValueField(.mouseEventDeltaX, value: Int64(point.x - last.x))
    event.setIntegerValueField(.mouseEventDeltaY, value: Int64(point.y - last.y))
    event.flags = args.contains("command") ? [.maskCommand] : []
    event.post(tap: .cghidEventTap)
    last = point
}

// Leave chrome hover targets before each gesture. Keep the pointer at the
// destination after release so a synthetic warp cannot race the WindowServer.
send(.mouseMoved, CGPoint(x: before.midX, y: before.midY))
Thread.sleep(forTimeInterval: 0.25)
guard let topmost = windows().first(where: {
    ($0[kCGWindowLayer as String] as? Int) == 0 && frame($0)?.contains(start) == true
}), topmost[kCGWindowNumber as String] as? Int == id else {
    fail("Fixture drag point \(start) is covered or outside its native window \(id) at \(before).")
}
send(.mouseMoved, start)
Thread.sleep(forTimeInterval: 0.25)
send(.leftMouseDown, start)
Thread.sleep(forTimeInterval: 0.12)

var end = start
if args.contains("drag") {
    let rapid = args.contains("rapid")
    let stepCount = rapid ? 20 : 10
    let stepSize = 40 / stepCount
    let direction = args.contains("left") ? -1 : 1
    for step in 1...stepCount {
        end.x = start.x + Double(step * stepSize * direction)
        send(.leftMouseDragged, end)
        Thread.sleep(forTimeInterval: rapid ? 0.008 : 0.04)
    }
} else if args.contains("slip") {
    end.x += 1
    send(.leftMouseDragged, end)
    Thread.sleep(forTimeInterval: 0.04)
}
send(.leftMouseUp, end)
Thread.sleep(forTimeInterval: 0.35)
guard let result = windows().first(where: { $0[kCGWindowNumber as String] as? Int == id }),
      let after = frame(result) else {
    fail("Fixture window disappeared during the gesture.")
}
let record: [String: Any] = [
    "window": id,
    "before": [before.minX, before.minY],
    "after": [after.minX, after.minY],
    "start": [start.x, start.y],
    "end": [end.x, end.y]
]
let data = try JSONSerialization.data(withJSONObject: record, options: [.sortedKeys])
print(String(decoding: data, as: UTF8.self))
