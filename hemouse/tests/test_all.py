"""
HEMouse Test Suite
Quick tests for all core components
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import time


def test_label_generator():
    """Test label generation"""
    print("\n" + "=" * 60)
    print("TEST: Label Generator")
    print("=" * 60)

    from core.label_generator import LabelGenerator

    gen = LabelGenerator()

    # Test 1: Single letters
    print("\n1. Testing single letter labels (9 elements)...")
    labels = gen.generate_labels(9)
    assert len(labels) == 9, f"Expected 9 labels, got {len(labels)}"
    assert labels == ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'], f"Unexpected labels: {labels}"
    print(f"   ✅ Generated: {labels}")

    # Test 2: Two letters
    print("\n2. Testing two letter labels (20 elements)...")
    labels = gen.generate_labels(20)
    assert len(labels) == 20, f"Expected 20 labels, got {len(labels)}"
    print(f"   ✅ Generated: {labels}")

    # Test 3: No prefix conflicts
    print("\n3. Testing for prefix conflicts...")
    labels = gen.generate_labels(50)
    for i, label1 in enumerate(labels):
        for j, label2 in enumerate(labels):
            if i != j:
                assert not label2.startswith(label1), f"Prefix conflict: {label1} vs {label2}"
    print(f"   ✅ No conflicts in {len(labels)} labels")

    # Test 4: Matching
    print("\n4. Testing label matching...")
    labels = gen.generate_labels(20)
    matches = gen.match_label("a", labels)
    print(f"   Input 'a' matches: {[labels[i] for i in matches]}")
    assert len(matches) > 0, "No matches found for 'a'"
    print(f"   ✅ Matching works")

    print("\n✅ Label Generator: ALL TESTS PASSED\n")


def test_mode_manager():
    """Test mode manager"""
    print("\n" + "=" * 60)
    print("TEST: Mode Manager")
    print("=" * 60)

    from modes.mode_manager import ModeManager, Mode

    manager = ModeManager()

    # Test initial state
    print("\n1. Testing initial state...")
    assert manager.get_current_mode() == Mode.IDLE, "Initial mode should be IDLE"
    print("   ✅ Initial mode: IDLE")

    # Test mode switching
    print("\n2. Testing mode switching...")

    callback_triggered = {'enter': False, 'exit': False}

    def on_hint_enter():
        callback_triggered['enter'] = True

    def on_hint_exit():
        callback_triggered['exit'] = True

    manager.register_callback('on_mode_enter', Mode.HINT, on_hint_enter)
    manager.register_callback('on_mode_exit', Mode.HINT, on_hint_exit)

    manager.switch_mode(Mode.HINT)
    assert manager.get_current_mode() == Mode.HINT, "Mode should be HINT"
    assert callback_triggered['enter'], "Enter callback not triggered"
    print("   ✅ Switched to HINT, callback triggered")

    manager.switch_mode(Mode.IDLE)
    assert manager.get_current_mode() == Mode.IDLE, "Mode should be IDLE"
    assert callback_triggered['exit'], "Exit callback not triggered"
    print("   ✅ Switched to IDLE, exit callback triggered")

    print("\n✅ Mode Manager: ALL TESTS PASSED\n")


def test_hotkey_manager():
    """Test hotkey manager (manual test)"""
    print("\n" + "=" * 60)
    print("TEST: Hotkey Manager (MANUAL)")
    print("=" * 60)

    from core.hotkey_manager import HotkeyManager

    print("\n⚠️ This is a manual test - requires user interaction")
    print("   Press CapsLock ON/OFF to test, or Ctrl+C to skip\n")

    manager = HotkeyManager()
    triggered = {'on': False, 'off': False}

    def on_capslock_on():
        print("   ✅ CapsLock ON detected")
        triggered['on'] = True

    def on_capslock_off():
        print("   ✅ CapsLock OFF detected")
        triggered['off'] = True

    manager.register_hotkey('capslock_on', on_capslock_on)
    manager.register_hotkey('capslock_off', on_capslock_off)
    manager.start_monitoring()

    print("   Press CapsLock now (10 seconds timeout)...")
    try:
        for i in range(20):
            time.sleep(0.5)
            if triggered['on'] or triggered['off']:
                break
    except KeyboardInterrupt:
        print("\n   ⚠️ Test skipped by user")

    manager.stop_monitoring()

    if triggered['on'] or triggered['off']:
        print("\n✅ Hotkey Manager: TEST PASSED\n")
    else:
        print("\n⚠️ Hotkey Manager: NO INTERACTION DETECTED\n")


def test_element_detector():
    """Test element detector (manual test)"""
    print("\n" + "=" * 60)
    print("TEST: Element Detector (MANUAL)")
    print("=" * 60)

    from core.element_detector import ElementDetector

    print("\n⚠️ This is a manual test - requires active window")
    print("   Make sure you have a window in focus (Chrome, VSCode, etc.)")

    response = input("\n   Press Enter to test, or 's' to skip: ")
    if response.lower() == 's':
        print("   ⚠️ Test skipped\n")
        return

    detector = ElementDetector()

    print("\n   Detecting elements...")
    start_time = time.time()
    elements = detector.get_clickable_elements()
    duration = time.time() - start_time

    print(f"\n   ✅ Detected {len(elements)} elements in {duration*1000:.0f}ms")

    if len(elements) > 0:
        print(f"\n   Sample elements (first 5):")
        for i, elem in enumerate(elements[:5]):
            print(f"   {i+1}. {elem['type']}: {elem['name'][:40]}")
        print("\n✅ Element Detector: TEST PASSED\n")
    else:
        print("\n   ⚠️ No elements detected (window may not be supported)\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("HEMouse Test Suite")
    print("=" * 60)

    try:
        # Automated tests
        test_label_generator()
        test_mode_manager()

        # Manual tests
        test_hotkey_manager()
        test_element_detector()

        print("\n" + "=" * 60)
        print("🎉 TEST SUITE COMPLETED")
        print("=" * 60)
        print("\n✅ All automated tests passed")
        print("⚠️ Manual tests require user interaction\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()