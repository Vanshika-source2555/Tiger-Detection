import javax.swing.*;
import java.awt.*;

public class AnalyticsPage extends JFrame {

    public AnalyticsPage() {
        setTitle("Analytics");
        setSize(500, 350);
        setLocationRelativeTo(null);
        setLayout(null);
        getContentPane().setBackground(new Color(245, 247, 250));

        JLabel title = new JLabel("Analytics", SwingConstants.CENTER);
        title.setFont(new Font("Segoe UI", Font.BOLD, 24));
        title.setForeground(new Color(0, 70, 130));
        title.setBounds(100, 25, 300, 40);
        add(title);

        JButton history = new JButton("Open History");
        history.setBounds(150, 100, 200, 45);
        styleButton(history);
        add(history);

        JButton stats = new JButton("Open Statistics");
        stats.setBounds(150, 170, 200, 45);
        styleButton(stats);
        add(stats);

        history.addActionListener(e -> new HistoryPage());
        stats.addActionListener(e -> new StatisticsPage());

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

        button.setBorder(
                BorderFactory.createLineBorder(
                        new Color(0, 105, 180),
                        2));
    }
}