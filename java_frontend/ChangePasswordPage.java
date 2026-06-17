import javax.swing.*;
import java.awt.*;

public class ChangePasswordPage extends JFrame {

    String email;
    JPasswordField oldPass;
    JPasswordField newPass;
    JPasswordField confirmPass;

    public ChangePasswordPage(String email) {
        this.email = email;

        setTitle("Change Password");
        setSize(460, 380);
        setLocationRelativeTo(null);
        setLayout(null);
        getContentPane().setBackground(new Color(245, 247, 250));

        JLabel title = new JLabel("Change Password", SwingConstants.CENTER);
        title.setFont(new Font("Segoe UI", Font.BOLD, 22));
        title.setForeground(new Color(0, 70, 130));
        title.setBounds(60, 25, 330, 35);
        add(title);

        JLabel oldLabel = new JLabel("Old Password:");
        oldLabel.setBounds(60, 90, 130, 25);
        add(oldLabel);

        oldPass = new JPasswordField();
        oldPass.setBounds(200, 90, 180, 28);
        add(oldPass);

        JLabel newLabel = new JLabel("New Password:");
        newLabel.setBounds(60, 140, 130, 25);
        add(newLabel);

        newPass = new JPasswordField();
        newPass.setBounds(200, 140, 180, 28);
        add(newPass);

        JLabel confirmLabel = new JLabel("Confirm Password:");
        confirmLabel.setBounds(60, 190, 130, 25);
        add(confirmLabel);

        confirmPass = new JPasswordField();
        confirmPass.setBounds(200, 190, 180, 28);
        add(confirmPass);

        JButton update = new JButton("Update Password");
        update.setBounds(90, 260, 170, 38);
        styleButton(update);
        add(update);

        JButton close = new JButton("Close");
        close.setBounds(280, 260, 100, 38);
        styleButton(close);
        add(close);

        update.addActionListener(e -> changePassword());
        close.addActionListener(e -> dispose());

        setVisible(true);
    }

    void changePassword() {
        String oldPassword = new String(oldPass.getPassword());
        String newPassword = new String(newPass.getPassword());
        String confirmPassword = new String(confirmPass.getPassword());

        if (oldPassword.isEmpty() || newPassword.isEmpty() || confirmPassword.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Please fill all fields");
            return;
        }

        if (!newPassword.equals(confirmPassword)) {
            JOptionPane.showMessageDialog(this, "New password and confirm password do not match");
            return;
        }

        String response = ApiClient.sendLoginData(
                "change_password",
                email,
                oldPassword + "," + newPassword);

        JOptionPane.showMessageDialog(this, response);

        if (response.toLowerCase().contains("success")) {
            dispose();
        }
    }

    void styleButton(JButton button) {
        button.setBackground(Color.WHITE);
        button.setForeground(Color.BLACK);
        button.setOpaque(true);
        button.setContentAreaFilled(true);
        button.setBorderPainted(true);
        button.setFocusPainted(false);
        button.setFont(new Font("Segoe UI", Font.BOLD, 13));
        button.setBorder(BorderFactory.createLineBorder(new Color(0, 105, 180), 2));
    }
}