
import javax.swing.*;
import java.awt.*;

public class HistoryPage extends JFrame {

    public HistoryPage() {
        setTitle("Detection History");
        setSize(700, 500);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout());

        JTextArea area = new JTextArea();
        area.setEditable(false);
        area.setFont(new Font("Arial", Font.PLAIN, 14));

        String historyData = ApiClient.sendAction("history");
        area.setText(historyData);

        add(new JScrollPane(area), BorderLayout.CENTER);

        setVisible(true);
    }
}