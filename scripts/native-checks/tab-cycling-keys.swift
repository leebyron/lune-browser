import AppKit
import CoreGraphics

let arguments = CommandLine.arguments
guard arguments.count == 5,
      let pid = Int32(arguments[1]),
      let count = Int(arguments[4]), count > 0,
      let application = NSRunningApplication(processIdentifier: pid),
      let source = CGEventSource(stateID: .hidSystemState) else {
    exit(2)
}

let modifier: (CGKeyCode, CGEventFlags)
let key: CGKeyCode
let shifts: Bool
switch (arguments[2], arguments[3]) {
case ("control", "next"):
    (modifier, key, shifts) = ((59, .maskControl), 48, false)
case ("control", "previous"):
    (modifier, key, shifts) = ((59, .maskControl), 48, true)
case ("bracket", "next"):
    (modifier, key, shifts) = ((55, .maskCommand), 30, true)
case ("bracket", "previous"):
    (modifier, key, shifts) = ((55, .maskCommand), 33, true)
default:
    exit(2)
}

application.activate()
let deadline = Date().addingTimeInterval(3)
while NSWorkspace.shared.frontmostApplication?.processIdentifier != pid {
    if Date() >= deadline {
        fputs("The fixture browser could not be brought to the foreground.\n", stderr)
        exit(1)
    }
    Thread.sleep(forTimeInterval: 0.05)
}

func post(_ key: CGKeyCode, down: Bool, flags: CGEventFlags, modifier: Bool = false) {
    guard let event = CGEvent(keyboardEventSource: source, virtualKey: key, keyDown: down) else {
        exit(1)
    }
    if modifier {
        event.type = .flagsChanged
    }
    event.flags = flags
    event.post(tap: .cghidEventTap)
    Thread.sleep(forTimeInterval: 0.055)
}

var flags = modifier.1
post(modifier.0, down: true, flags: flags, modifier: true)
if shifts {
    flags.insert(.maskShift)
    post(56, down: true, flags: flags, modifier: true)
}
for _ in 0..<count {
    post(key, down: true, flags: flags)
    post(key, down: false, flags: flags)
}
if shifts {
    flags.remove(.maskShift)
    post(56, down: false, flags: flags, modifier: true)
}
post(modifier.0, down: false, flags: [], modifier: true)
