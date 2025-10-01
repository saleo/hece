"""
Gaze Tracking MVP - Standalone Application
双屏目光追踪窗口自动激活 - 独立测试程序

Usage:
    python gaze_tracker_standalone.py --calibrate  # 校准模式
    python gaze_tracker_standalone.py --run        # 运行模式
    python gaze_tracker_standalone.py --test       # 测试模式（显示Yaw角度）
    python gaze_tracker_standalone.py --info       # 显示配置信息
"""

import sys
import time
import argparse
from modules.gaze_tracker import GazeTracker
import cv2


def print_banner():
    """打印程序横幅"""
    print("\n" + "=" * 60)
    print(" " * 10 + "🎯 Gaze Tracking MVP - Phase 1")
    print(" " * 10 + "双屏目光追踪窗口自动激活")
    print("=" * 60 + "\n")


def calibrate_mode(tracker):
    """校准模式"""
    print("📍 Calibration Mode")
    print("=" * 60)

    # 显示屏幕布局
    tracker.calibrator.print_screen_layout()

    # 检查屏幕数量
    num_screens = tracker.calibrator.screen_layout["total_screens"]
    if num_screens < 2:
        print("\n⚠️  Warning: Only 1 screen detected")
        print("   Gaze tracking requires at least 2 screens")
        print("   You can still calibrate for testing purposes")

    # 校准主屏
    print("\n" + "=" * 60)
    print("Step 1: Calibrate Primary Screen")
    print("=" * 60)
    input("\nPress Enter when you are ready to start...")

    result = tracker.calibrate_screen("primary", duration=5)

    if not result["success"]:
        print(f"\n❌ Primary calibration failed: {result.get('error', 'Unknown error')}")
        return False

    # 校准副屏（如果有）
    if num_screens > 1:
        for i in range(num_screens - 1):
            screen_name = f"secondary_{i}"

            print("\n" + "=" * 60)
            print(f"Step {i+2}: Calibrate Secondary Screen {i}")
            print("=" * 60)
            input("\nPress Enter when you are ready to start...")

            result = tracker.calibrate_screen(screen_name, duration=5)

            if not result["success"]:
                print(f"\n⚠️  Secondary {i} calibration failed: {result.get('error', 'Unknown error')}")
                print("   You can skip this and re-calibrate later")

    # 显示校准结果
    print("\n" + "=" * 60)
    print("✅ Calibration Complete!")
    print("=" * 60)

    tracker.calibrator.print_calibration_info()

    print("\n💡 Next Steps:")
    print("   Run: python gaze_tracker_standalone.py --run")
    print("   Or test: python gaze_tracker_standalone.py --test")

    return True


def run_mode(tracker):
    """运行模式 - 实际追踪并激活窗口"""
    print("🚀 Run Mode - Gaze Tracking Active")
    print("=" * 60)

    # 检查校准状态
    status = tracker.calibrator.get_calibration_status()
    if status["calibrated_screens"] == 0:
        print("❌ No calibration data found")
        print("   Please run calibration first:")
        print("   python gaze_tracker_standalone.py --calibrate")
        return False

    # 显示校准信息
    tracker.calibrator.print_calibration_info()

    # 启动追踪
    if not tracker.start_tracking():
        print("❌ Failed to start tracking")
        return False

    print("\n" + "=" * 60)
    print("✅ Tracking Active")
    print("=" * 60)
    print("\n📖 Instructions:")
    print("   - Move your head to look at different screens")
    print("   - Windows on the target screen will be auto-activated")
    print("   - Press Ctrl+C to stop\n")

    try:
        # 主循环
        last_stats_time = time.time()
        stats_interval = 10  # 每10秒打印一次统计

        while True:
            time.sleep(1)

            # 定期打印统计
            if time.time() - last_stats_time >= stats_interval:
                stats = tracker.get_stats()
                print(f"\n📊 Stats: {stats['frames_processed']} frames, "
                      f"{stats['screen_switches']} switches, "
                      f"{stats['processing_fps']:.1f} FPS")
                last_stats_time = time.time()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")

    finally:
        tracker.stop_tracking()
        tracker.print_stats()

    return True


def test_mode(tracker):
    """测试模式 - 显示实时Yaw角度（不激活窗口）"""
    print("🧪 Test Mode - Visual Feedback")
    print("=" * 60)

    # 启动摄像头
    if not tracker.camera.start():
        print("❌ Failed to start camera")
        return False

    print("\n✅ Camera started")
    print("\n📖 Instructions:")
    print("   - A window will show your Yaw angle in real-time")
    print("   - Move your head left/right to see the angle change")
    print("   - The thresholds (if calibrated) will be shown")
    print("   - Press 'q' to quit\n")

    input("Press Enter to start visual test...")

    # 获取校准信息
    calibration = tracker.calibrator.calibration

    try:
        while True:
            frame = tracker.camera.get_latest_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            # 估计姿态
            pose = tracker.pose_estimator.estimate_pose(frame)

            # 创建显示帧
            display_frame = cv2.resize(frame, (640, 480))

            if pose:
                yaw = pose['yaw']
                yaw_smoothed = pose['yaw_smoothed']
                pitch = pose['pitch']
                roll = pose['roll']

                # 绘制姿态信息
                y_offset = 30
                cv2.putText(display_frame, f"Yaw (Raw):     {yaw:.1f} deg",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                           0.6, (255, 255, 255), 2)

                y_offset += 30
                cv2.putText(display_frame, f"Yaw (Smoothed): {yaw_smoothed:.1f} deg",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                           0.6, (0, 255, 255), 2)

                y_offset += 30
                cv2.putText(display_frame, f"Pitch:         {pitch:.1f} deg",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                           0.6, (200, 200, 200), 1)

                y_offset += 30
                cv2.putText(display_frame, f"Roll:          {roll:.1f} deg",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                           0.6, (200, 200, 200), 1)

                # 判断目标屏幕
                target_screen = tracker.calibrator.determine_target_screen(yaw_smoothed)

                # 显示校准阈值（如果有）
                y_offset += 50
                if calibration:
                    for screen_name, calib in calibration.items():
                        color = (0, 255, 0) if target_screen == screen_name else (100, 100, 100)
                        text = f"{screen_name}: {calib['threshold_low']:.0f} ~ {calib['threshold_high']:.0f}"
                        cv2.putText(display_frame, text,
                                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                                   0.5, color, 1)
                        y_offset += 25

                # 显示当前目标屏幕
                y_offset += 20
                if target_screen:
                    screen_text = f"TARGET: {target_screen.upper()}"
                    color = (0, 255, 0)
                else:
                    screen_text = "TARGET: None (between screens)"
                    color = (0, 0, 255)

                cv2.putText(display_frame, screen_text,
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                           0.8, color, 2)

                # 方向指示箭头
                y_offset = display_frame.shape[0] - 50
                if yaw_smoothed < -15:
                    direction = "<<< LEFT"
                    color = (255, 0, 0)
                elif yaw_smoothed > 15:
                    direction = "RIGHT >>>"
                    color = (0, 0, 255)
                else:
                    direction = "CENTER"
                    color = (0, 255, 0)

                cv2.putText(display_frame, direction,
                           (display_frame.shape[1] // 2 - 100, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX,
                           1.0, color, 3)

            else:
                cv2.putText(display_frame, "No face detected",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                           1.0, (0, 0, 255), 2)

            # 显示帧
            cv2.imshow('Gaze Tracking Test', display_frame)

            # 按q退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")

    finally:
        tracker.camera.stop()
        cv2.destroyAllWindows()

    print("\n👋 Test complete")
    return True


def info_mode(tracker):
    """信息模式 - 显示配置和状态"""
    print("ℹ️  Info Mode")
    print("=" * 60)

    # 屏幕布局
    tracker.calibrator.print_screen_layout()

    # 校准状态
    status = tracker.calibrator.get_calibration_status()
    print("\n📊 Calibration Status:")
    print(f"   Total screens: {status['total_screens']}")
    print(f"   Calibrated screens: {status['calibrated_screens']}")

    for screen_name, info in status['screens'].items():
        if info['exists']:
            status_str = "✅ Calibrated" if info['calibrated'] else "⚠️ Not calibrated"
            print(f"   {screen_name}: {status_str}")

    # 详细校准信息
    if status['calibrated_screens'] > 0:
        tracker.calibrator.print_calibration_info()
    else:
        print("\n⚠️  No calibration data found")
        print("   Run: python gaze_tracker_standalone.py --calibrate")

    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Gaze Tracking MVP - Phase 1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gaze_tracker_standalone.py --calibrate   # 校准屏幕
  python gaze_tracker_standalone.py --run         # 运行追踪
  python gaze_tracker_standalone.py --test        # 测试模式
  python gaze_tracker_standalone.py --info        # 显示信息
        """
    )

    parser.add_argument('--calibrate', action='store_true',
                       help='Run calibration mode')
    parser.add_argument('--run', action='store_true',
                       help='Run tracking mode')
    parser.add_argument('--test', action='store_true',
                       help='Run test mode (visual feedback)')
    parser.add_argument('--info', action='store_true',
                       help='Show configuration info')
    parser.add_argument('--config', default='config/gaze_config.json',
                       help='Path to config file (default: config/gaze_config.json)')

    args = parser.parse_args()

    # 打印横幅
    print_banner()

    # 初始化追踪器
    try:
        tracker = GazeTracker(config_path=args.config)
    except Exception as e:
        print(f"❌ Failed to initialize tracker: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # 执行对应模式
    try:
        if args.calibrate:
            success = calibrate_mode(tracker)
        elif args.run:
            success = run_mode(tracker)
        elif args.test:
            success = test_mode(tracker)
        elif args.info:
            success = info_mode(tracker)
        else:
            # 默认显示帮助
            parser.print_help()
            success = True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
