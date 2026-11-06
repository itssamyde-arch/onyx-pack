package de.onyx.textures;

import org.bukkit.ChatColor;
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.plugin.java.JavaPlugin;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * ONYX Textures - schickt das ONYX Resource-Pack (Portal-Textur + Logo fuer das Regel-Fenster)
 * an Spieler. Befehle: /onyxpack send [Spieler] | reload | status
 */
public final class OnyxTextures extends JavaPlugin implements Listener {

    private String url;
    private String sha1;
    private boolean force;
    private boolean sendOnJoin;

    @Override
    public void onEnable() {
        saveDefaultConfig();
        loadSettings();
        getServer().getPluginManager().registerEvents(this, this);
        if (url.isEmpty()) {
            getLogger().warning("pack-url ist leer. Trage in plugins/OnyxTextures/config.yml die Adresse deines Packs ein.");
        } else {
            getLogger().info("Pack wird an Spieler gesendet: " + url);
        }
    }

    private void loadSettings() {
        reloadConfig();
        url = getConfig().getString("pack-url", "").trim();
        sha1 = getConfig().getString("sha1", "").trim().toLowerCase(Locale.ROOT);
        force = getConfig().getBoolean("force", false);
        sendOnJoin = getConfig().getBoolean("send-on-join", true);
    }

    private boolean ready() {
        return !url.isEmpty() && sha1.length() == 40;
    }

    @SuppressWarnings("deprecation")
    private void sendPack(Player p) {
        if (!ready()) {
            return;
        }
        p.setResourcePack(url, sha1, force);
    }

    @EventHandler
    public void onJoin(PlayerJoinEvent e) {
        if (!sendOnJoin || !ready()) {
            return;
        }
        Player p = e.getPlayer();
        // kurz warten, bis der Spieler komplett geladen ist
        getServer().getScheduler().runTaskLater(this, () -> {
            if (p.isOnline()) {
                sendPack(p);
            }
        }, 40L);
    }

    @Override
    public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
        String prefix = ChatColor.DARK_PURPLE + "" + ChatColor.BOLD + "ONYX " + ChatColor.DARK_GRAY + "» " + ChatColor.GRAY;
        if (!sender.hasPermission("onyx.admin")) {
            sender.sendMessage(prefix + ChatColor.RED + "Dazu hast du keine Rechte.");
            return true;
        }
        String sub = args.length > 0 ? args[0].toLowerCase(Locale.ROOT) : "status";
        switch (sub) {
            case "reload":
                loadSettings();
                sender.sendMessage(prefix + "Konfiguration neu geladen.");
                return true;
            case "send": {
                if (!ready()) {
                    sender.sendMessage(prefix + ChatColor.RED + "pack-url oder sha1 in der config.yml fehlt.");
                    return true;
                }
                if (args.length > 1) {
                    Player target = getServer().getPlayerExact(args[1]);
                    if (target == null) {
                        sender.sendMessage(prefix + ChatColor.RED + "Spieler nicht gefunden.");
                        return true;
                    }
                    sendPack(target);
                    sender.sendMessage(prefix + "Pack an " + target.getName() + " gesendet.");
                } else if (sender instanceof Player) {
                    sendPack((Player) sender);
                    sender.sendMessage(prefix + "Pack gesendet.");
                } else {
                    for (Player p : getServer().getOnlinePlayers()) {
                        sendPack(p);
                    }
                    sender.sendMessage(prefix + "Pack an alle Spieler gesendet.");
                }
                return true;
            }
            default:
                sender.sendMessage(prefix + "URL: " + (url.isEmpty() ? ChatColor.RED + "nicht gesetzt" : ChatColor.LIGHT_PURPLE + url));
                sender.sendMessage(prefix + "SHA1: " + ChatColor.LIGHT_PURPLE + (sha1.isEmpty() ? "-" : sha1));
                sender.sendMessage(prefix + "Beim Beitritt senden: " + ChatColor.LIGHT_PURPLE + sendOnJoin + ChatColor.GRAY + ", erzwingen: " + ChatColor.LIGHT_PURPLE + force);
                return true;
        }
    }

    @Override
    public List<String> onTabComplete(CommandSender sender, Command cmd, String alias, String[] args) {
        List<String> out = new ArrayList<>();
        if (args.length == 1) {
            for (String s : new String[]{"send", "reload", "status"}) {
                if (s.startsWith(args[0].toLowerCase(Locale.ROOT))) {
                    out.add(s);
                }
            }
        }
        return out;
    }
}
