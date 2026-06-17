import javax.swing.*;
import java.awt.*;

public class ProfilePage extends JFrame {

    public ProfilePage(String email) {
        setTitle("User Profile");
        setSize(400, 280);
        setLocationRelativeTo(null);
        setLayout(null);
        getContentPane().setBackground(new Color(245, 247, 250));

        JLabel title = new JLabel("Profile", SwingConstants.CENTER);
        title.setFont(new Font("Segoe UI", Font.BOLD, 22));
        title.setBounds(60, 30, 280, 35);
        add(title);

        JLabel emailLabel = new JLabel("Email ID:");
        emailLabel.setBounds(70, 100, 100, 25);
        add(emailLabel);

        JLabel emailValue = new JLabel(email);
        emailValue.setBounds(150, 100, 220, 25);
        add(emailValue);

        JLabel status = new JLabel("Account Status: Active");
        status.setBounds(70, 145, 250, 25);
        add(status);

        JButton close = new JButton("Close");
        close.setBounds(140, 190, 120, 35);
        styleButton(close);
        add(close);

        close.addActionListener(e -> dispose());

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