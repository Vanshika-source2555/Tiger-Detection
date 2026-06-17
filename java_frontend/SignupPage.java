import javax.swing.*;
import java.awt.*;

public class SignupPage extends JFrame {

    JTextField emailField;
    JPasswordField passwordField;
    JPasswordField confirmPasswordField;

    public SignupPage() {
        setTitle("Tiger Detection - Sign Up");
        setSize(470, 360);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(null);
        getContentPane().setBackground(new Color(245, 247, 250));

        JLabel title = new JLabel("Create New Account", SwingConstants.CENTER);
        title.setFont(new Font("Segoe UI", Font.BOLD, 22));
        title.setBounds(70, 30, 330, 35);
        add(title);

        JLabel emailLabel = new JLabel("Email ID:");
        emailLabel.setBounds(65, 100, 130, 25);
        add(emailLabel);

        emailField = new JTextField();
        emailField.setBounds(200, 100, 210, 28);
        add(emailField);

        JLabel passLabel = new JLabel("Password:");
        passLabel.setBounds(65, 145, 130, 25);
        add(passLabel);

        passwordField = new JPasswordField();
        passwordField.setBounds(200, 145, 210, 28);
        add(passwordField);

        JLabel confirmLabel = new JLabel("Confirm Password:");
        confirmLabel.setBounds(65, 190, 130, 25);
        add(confirmLabel);

        confirmPasswordField = new JPasswordField();
        confirmPasswordField.setBounds(200, 190, 210, 28);
        add(confirmPasswordField);

        JButton signupButton = new JButton("Sign Up");
        signupButton.setBounds(95, 250, 130, 35);
        styleButton(signupButton);
        add(signupButton);

        JButton backButton = new JButton("Back");
        backButton.setBounds(245, 250, 130, 35);
        styleButton(backButton);
        add(backButton);

        signupButton.addActionListener(e -> signupUser());

        backButton.addActionListener(e -> {
            dispose();
            new LoginPage();
        });

        setVisible(true);
    }

    void signupUser() {
        String email = emailField.getText().trim();
        String password = new String(passwordField.getPassword());
        String confirmPassword = new String(confirmPasswordField.getPassword());

        if (email.isEmpty() || password.isEmpty() || confirmPassword.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Please fill all fields");
            return;
        }

        if (!email.contains("@") || !email.contains(".")) {
            JOptionPane.showMessageDialog(this, "Please enter a valid email ID");
            return;
        }

        if (!password.equals(confirmPassword)) {
            JOptionPane.showMessageDialog(this, "Passwords do not match");
            return;
        }

        String response = ApiClient.sendLoginData("signup", email, password);
        JOptionPane.showMessageDialog(this, response);

        if (response.toLowerCase().contains("success")) {
            dispose();
            new LoginPage();
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