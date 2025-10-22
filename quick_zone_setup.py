#!/usr/bin/env python3
"""
Quick Zone Setup - Ultra-fast zone configuration
Takes a single snapshot and lets you draw zones on it (no video lag)
"""

import cv2
import json
import numpy as np
from pathlib import Path


def quick_setup():
    """Quick zone setup using snapshot"""

    print("\n" + "=" * 60)
    print("⚡ Quick Zone Setup - Versão Rápida")
    print("=" * 60)

    # Load camera config
    camera_index = 0
    user_config_file = Path(__file__).parent / 'user_config.json'
    if user_config_file.exists():
        try:
            with open(user_config_file, 'r') as f:
                config = json.load(f)
                camera_index = config.get('camera_index', 0)
        except:
            pass

    print(f"\n1. Capturando foto da câmera {camera_index}...")

    # Capture single frame
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("❌ Erro ao abrir câmera!")
        return False

    # Wait for camera to warm up
    for _ in range(10):
        cap.read()

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Erro ao capturar foto!")
        return False

    print("✅ Foto capturada!")

    # Variables
    zones = []
    points = []
    drawing = False

    def mouse_callback(event, x, y, flags, param):
        nonlocal points, drawing

        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            points = [(x, y)]

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                points = [points[0], (x, y)]

        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            if len(points) == 2:
                x1, y1 = points[0]
                x2, y2 = points[1]

                zone = {
                    'name': f'Zona {len(zones) + 1}',
                    'points': [(x1, y1), (x2, y1), (x2, y2), (x1, y2)],
                    'color': [0, 0, 255],  # Red
                    'type': 'forbidden'
                }
                zones.append(zone)
                points = []
                print(f"✅ Zona {len(zones)} criada!")

    # Setup window
    window_name = "⚡ Quick Setup - Desenhe o Sofá"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)

    print("\n2. Desenhando zonas...")
    print("\nInstruções:")
    print("  • Clique e arraste para desenhar o SOFÁ")
    print("  • Pressione 'S' para SALVAR")
    print("  • Pressione 'C' para LIMPAR")
    print("  • Pressione 'Q' para CANCELAR")
    print("=" * 60 + "\n")

    while True:
        display = frame.copy()

        # Draw existing zones
        overlay = display.copy()
        for zone in zones:
            pts = np.array(zone['points'], dtype=np.int32)
            cv2.fillPoly(overlay, [pts], zone['color'])
            cv2.polylines(display, [pts], True, zone['color'], 3)

            x, y = zone['points'][0]
            cv2.putText(display, zone['name'], (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, zone['color'], 2)

        cv2.addWeighted(overlay, 0.3, display, 0.7, 0, display)

        # Draw current zone being drawn
        if drawing and len(points) == 2:
            x1, y1 = points[0]
            x2, y2 = points[1]
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 3)

        # Draw instructions on image
        cv2.putText(display, f"Zonas: {len(zones)} | S=Salvar | C=Limpar | Q=Cancelar",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display, f"Zonas: {len(zones)} | S=Salvar | C=Limpar | Q=Cancelar",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)

        cv2.imshow(window_name, display)

        key = cv2.waitKey(10) & 0xFF

        if key == ord('q'):
            print("\n❌ Cancelado")
            cv2.destroyAllWindows()
            return False

        elif key == ord('c'):
            zones = []
            print("\n🗑️  Zonas limpas")

        elif key == ord('s'):
            if len(zones) == 0:
                print("\n⚠️  Crie pelo menos uma zona!")
                continue

            # Save zones in src/ directory (where zone_detector.py runs)
            config_file = Path(__file__).parent / 'src' / 'zone_config.json'
            config_file_root = Path(__file__).parent / 'zone_config.json'

            config = {
                'zones': zones,
                'camera_index': camera_index
            }

            # Save in both locations for compatibility
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            with open(config_file_root, 'w') as f:
                json.dump(config, f, indent=2)

            print(f"\n💾 {len(zones)} zona(s) salva(s)!")
            print(f"   - {config_file}")
            print(f"   - {config_file_root}")
            cv2.destroyAllWindows()
            return True

    cv2.destroyAllWindows()
    return False


def main():
    """Entry point"""
    try:
        if quick_setup():
            print("\n✅ Setup concluído!")
            print("\nInicie o detector:")
            print("  cd src && python zone_detector.py\n")
        else:
            print("\n👋 Cancelado.\n")

    except KeyboardInterrupt:
        print("\n\n👋 Cancelado.\n")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
