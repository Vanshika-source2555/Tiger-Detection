import javax.swing.*;
import java.awt.*;

public class LoginPage extends JFrame {

    JTextField emailField;
    JPasswordField passwordField;

    public LoginPage() {
        setTitle("Tiger Detection - Login");
        setSize(430, 340);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(null);
        getContentPane().setBackground(new Color(245, 247, 250));

        JLabel title = new JLabel("User Login", SwingConstants.CENTER);
        title.setFont(new Font("Segoe UI", Font.BOLD, 24));
        title.setBounds(70, 30, 280, 35);
        add(title);

        JLabel emailLabel = new JLabel("Email ID:");
        emailLabel.setBounds(60, 100, 100, 25);
        add(emailLabel);

        emailField = new JTextField();
        emailField.setBounds(160, 100, 200, 28);
        add(emailField);

        JLabel passLabel = new JLabel("Password:");
        passLabel.setBounds(60, 145, 100, 25);
        add(passLabel);

        passwordField = new JPasswordField();
        passwordField.setBounds(160, 145, 200, 28);
        add(passwordField);

        JButton loginButton = new JButton("Login");
        loginButton.setBounds(80, 210, 120, 35);
        styleButton(loginButton);
        add(loginButton);

        JButton signupButton = new JButton("Sign Up");
        signupButton.setBounds(220, 210, 120, 35);
        styleButton(signupButton);
        add(signupButton);

        loginButton.addActionListener(e -> loginUser());

        signupButton.addActionListener(e -> {
            dispose();
            new SignupPage();
        });

        setVisible(true);
    }

    void loginUser() {
        String email = emailField.getText().trim();
        String password = new String(passwordField.getPassword());

        if (email.isEmpty() || password.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Please enter email and password");
            return;
        }

        String response = ApiClient.sendLoginData("login", email, password);

        if (response.equalsIgnoreCase("success")) {
            JOptionPane.showMessageDialog(this, "Login successful");
            dispose();
            new DashboardPage(email);
        } else {
            JOptionPane.showMessageDialog(this, response);
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