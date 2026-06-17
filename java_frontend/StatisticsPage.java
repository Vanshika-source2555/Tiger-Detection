
import javax.swing.*;
import java.awt.*;

public class StatisticsPage extends JFrame {

    public StatisticsPage() {
        setTitle("Detection Statistics");
        setSize(500, 400);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout());

        JTextArea area = new JTextArea();
        area.setEditable(false);
        area.setFont(new Font("Arial", Font.BOLD, 16));

        String statsData = ApiClient.sendAction("stats");
        area.setText(statsData);

        add(new JScrollPane(area), BorderLayout.CENTER);

        setVisible(true);
    }
}