import javax.swing.*;
import java.awt.*;

public class AIAssistantPage extends JDialog {

    JTextField questionField;
    JTextArea answerArea;
    DashboardPage dashboard;

    public AIAssistantPage(DashboardPage parent) {

        super(parent, "Assistant", false);

        this.dashboard = parent;

        setSize(400, 700);

        setLocation(
                parent.getX() + parent.getWidth() - 420,
                parent.getY());

        setLayout(null);
        getContentPane().setBackground(new Color(245, 247, 250));

        JLabel title = new JLabel("Assistant");
        title.setFont(new Font("Segoe UI", Font.BOLD, 24));
        title.setBounds(80, 20, 250, 40);
        add(title);

        JLabel subtitle = new JLabel("Ask anything about Tiger Detection");
        subtitle.setBounds(60, 60, 300, 30);
        add(subtitle);

        questionField = new JTextField();
        questionField.setBounds(20, 120, 280, 45);
        add(questionField);

        JButton sendButton = new JButton(">");
        sendButton.setBounds(315, 120, 50, 45);
        sendButton.setBackground(new Color(0, 120, 215));
        sendButton.setForeground(Color.WHITE);
        sendButton.setFont(new Font("Segoe UI", Font.BOLD, 20));
        sendButton.setFocusPainted(false);
        add(sendButton);

        answerArea = new JTextArea();
        answerArea.setEditable(false);
        answerArea.setLineWrap(true);
        answerArea.setWrapStyleWord(true);
        answerArea.setFont(new Font("Segoe UI", Font.PLAIN, 14));

        JScrollPane scrollPane = new JScrollPane(answerArea);
        scrollPane.setBounds(20, 190, 350, 450);
        add(scrollPane);

        sendButton.addActionListener(e -> askAI());

        setVisible(true);
    }

    void askAI() {

        String question = questionField.getText().trim();

        if (question.equals("")) {
            JOptionPane.showMessageDialog(this, "Enter a question");
            return;
        }

        answerArea.setText("Thinking...");

        String response = dashboard.callPostApi(
                "http://127.0.0.1:5000/ai_chat",
                "question=" + dashboard.encode(question));

        answerArea.setText(response);
    }
}