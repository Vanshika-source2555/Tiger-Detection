import javax.swing.*;
import java.awt.*;

public class AccountPage extends JFrame {

    String email;

    public AccountPage(String email) {
        this.email = email;

        setTitle("Account");
        setSize(400, 280);
        setLocationRelativeTo(null);
        setLayout(null);
        getContentPane().setBackground(new Color(245, 247, 250));

        JLabel title = new JLabel("Account Settings", SwingConstants.CENTER);
        title.setFont(new Font("Segoe UI", Font.BOLD, 22));
        title.setBounds(50, 25, 300, 35);
        add(title);

        JLabel emailLabel = new JLabel("Email: " + email, SwingConstants.CENTER);
        emailLabel.setBounds(40, 80, 320, 25);
        add(emailLabel);

        JButton profile = new JButton("Profile");
        profile.setBounds(110, 130, 170, 35);
        styleButton(profile);
        add(profile);

        JButton changePassword = new JButton("Change Password");
        changePassword.setBounds(110, 180, 170, 35);
        styleButton(changePassword);
        add(changePassword);

        profile.addActionListener(e -> new ProfilePage(email));
        changePassword.addActionListener(e -> new ChangePasswordPage(email));

        setVisible(true);
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