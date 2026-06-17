
import javax.swing.UIManager;

public class Main {

    public static void main(String[] args) {

        try {
            // Use system look and feel
            UIManager.setLookAndFeel(
                    UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }

        // Open Login Page
        new LoginPage();

    }
}