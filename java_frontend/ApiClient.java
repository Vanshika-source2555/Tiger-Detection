import java.io.*;
import java.net.*;

public class ApiClient {

    static String API_URL = "http://127.0.0.1:5000/api";

    public static String sendLoginData(String action, String email, String password) {
        try {
            URL url = new URL(API_URL);
            HttpURLConnection con = (HttpURLConnection) url.openConnection();

            con.setRequestMethod("POST");
            con.setDoOutput(true);
            con.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");

            String data = "action=" + URLEncoder.encode(action, "UTF-8") +
                    "&email=" + URLEncoder.encode(email, "UTF-8") +
                    "&password=" + URLEncoder.encode(password, "UTF-8");

            OutputStream os = con.getOutputStream();
            os.write(data.getBytes());
            os.flush();
            os.close();

            return readResponse(con);

        } catch (Exception e) {
            return "Backend not running: " + e.getMessage();
        }
    }

    public static String sendAction(String action) {
        try {
            URL url = new URL(API_URL);
            HttpURLConnection con = (HttpURLConnection) url.openConnection();

            con.setRequestMethod("POST");
            con.setDoOutput(true);
            con.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");

            String data = "action=" + URLEncoder.encode(action, "UTF-8");

            OutputStream os = con.getOutputStream();
            os.write(data.getBytes());
            os.flush();
            os.close();

            return readResponse(con);

        } catch (Exception e) {
            return "Backend not running: " + e.getMessage();
        }
    }

    public static String sendFile(String action, File file) {
        try {
            String boundary = "----TigerBoundary";
            URL url = new URL(API_URL);

            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setDoOutput(true);
            con.setRequestMethod("POST");
            con.setRequestProperty("Content-Type", "multipart/form-data; boundary=" + boundary);

            DataOutputStream out = new DataOutputStream(con.getOutputStream());

            out.writeBytes("--" + boundary + "\r\n");
            out.writeBytes("Content-Disposition: form-data; name=\"action\"\r\n\r\n");
            out.writeBytes(action + "\r\n");

            out.writeBytes("--" + boundary + "\r\n");
            out.writeBytes("Content-Disposition: form-data; name=\"file\"; filename=\"" + file.getName() + "\"\r\n");
            out.writeBytes("Content-Type: application/octet-stream\r\n\r\n");

            FileInputStream input = new FileInputStream(file);
            byte[] buffer = new byte[4096];
            int bytesRead;

            while ((bytesRead = input.read(buffer)) != -1) {
                out.write(buffer, 0, bytesRead);
            }

            input.close();

            out.writeBytes("\r\n--" + boundary + "--\r\n");
            out.flush();
            out.close();

            return readResponse(con);

        } catch (Exception e) {
            return "Error connecting to backend: " + e.getMessage();
        }
    }

    private static String readResponse(HttpURLConnection con) {
        try {
            InputStream stream;

            if (con.getResponseCode() >= 200 && con.getResponseCode() < 300) {
                stream = con.getInputStream();
            } else {
                stream = con.getErrorStream();
            }

            BufferedReader br = new BufferedReader(new InputStreamReader(stream));

            String line;
            StringBuilder response = new StringBuilder();

            while ((line = br.readLine()) != null) {
                response.append(line).append("\n");
            }

            br.close();

            return response.toString().trim();

        } catch (Exception e) {
            return "No response from backend: " + e.getMessage();
        }
    }
}