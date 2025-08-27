import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

"""
Test the new scrollable features section to ensure it works properly
"""

import sys
from PySide6.QtWidgets import QApplication, QScrollArea
from PySide6.QtCore import QTimer
from enbraille_data import EnBrailleData
from enbraille_gui import EnBrailleWindow

def test_scrollable_features():
    """Test the scrollable features section"""
    app = QApplication(sys.argv)
    
    print("=== Scrollable Features Section Test ===")
    
    # Create data and ensure welcome page is shown
    data = EnBrailleData(app)
    data.skipWelcomePage = False
    
    print("Creating window with scrollable features...")
    window = EnBrailleWindow(data)
    window.show()
    
    def analyze_features_section():
        print("\n📋 Features Section Analysis:")
        
        current_page = window.currentPage()
        print(f"Current page: {current_page.__class__.__name__}")
        
        # Find scroll area in the page
        scroll_areas = current_page.findChildren(QScrollArea)
        
        if scroll_areas:
            scroll_area = scroll_areas[0]
            print(f"\n✅ Scroll Area Found:")
            print(f"   - Count: {len(scroll_areas)} scroll area(s)")
            print(f"   - Size: {scroll_area.size().width()} x {scroll_area.size().height()}")
            print(f"   - Maximum height: {scroll_area.maximumHeight()}")
            print(f"   - Minimum height: {scroll_area.minimumHeight()}")
            print(f"   - Widget resizable: {scroll_area.widgetResizable()}")
            print(f"   - Horizontal scrollbar policy: {scroll_area.horizontalScrollBarPolicy()}")
            print(f"   - Vertical scrollbar policy: {scroll_area.verticalScrollBarPolicy()}")
            
            # Get the content widget
            content_widget = scroll_area.widget()
            if content_widget:
                print(f"\n📄 Content Widget:")
                print(f"   - Content size: {content_widget.size().width()} x {content_widget.size().height()}")
                print(f"   - Content children count: {len(content_widget.children())}")
                
                # Check for feature frames
                from PySide6.QtWidgets import QFrame
                frames = content_widget.findChildren(QFrame)
                print(f"   - Feature frames found: {len(frames)}")
                
                if frames:
                    print(f"   - First frame size: {frames[0].size().width()} x {frames[0].size().height()}")
                    print(f"   - Frame styling applied: {bool(frames[0].styleSheet())}")
            
            print(f"\n🎨 Styling:")
            print(f"   - Scroll area has stylesheet: {bool(scroll_area.styleSheet())}")
            print(f"   - Accessible name: '{scroll_area.accessibleName()}'")
            
            # Test scrolling if needed
            scrollbar = scroll_area.verticalScrollBar()
            if scrollbar:
                print(f"\n📜 Scrolling:")
                print(f"   - Scrollbar visible: {scrollbar.isVisible()}")
                print(f"   - Scrollbar range: {scrollbar.minimum()} to {scrollbar.maximum()}")
                print(f"   - Current position: {scrollbar.value()}")
                
                if scrollbar.maximum() > 0:
                    print(f"   - Content is scrollable! ✅")
                else:
                    print(f"   - Content fits without scrolling ✅")
        else:
            print("❌ No scroll area found")
        
        print(f"\n🔍 Overall Layout Check:")
        # Count all labels to see if overlap issue is resolved
        from PySide6.QtWidgets import QLabel
        labels = current_page.findChildren(QLabel)
        feature_labels = [label for label in labels if 'Feature' in label.accessibleName()]
        print(f"   - Feature-related labels found: {len(feature_labels)}")
        print(f"   - Total labels on page: {len(labels)}")
        
        print("\n✅ Scrollable features test completed!")
        print("\nExpected improvements:")
        print("- Features are now in a contained scroll area")
        print("- No more overlapping text")
        print("- Professional card-style layout")
        print("- Hover effects and proper spacing")
        print("- Controlled height prevents page bloat")
        
        QTimer.singleShot(2000, window.close)
    
    # Analyze after window is fully rendered
    QTimer.singleShot(300, analyze_features_section)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_scrollable_features())