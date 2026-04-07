# ── APO Sub-Components for Likud over time ─────────────────────────────────
# Requires: tidyverse, ggplot2
# Data:     V-Dem-CPD-Party-V2.csv (V-Party v2)

library(tidyverse)

# ── Load & filter ────────────────────────────────────────────────────────────
df <- read_csv("V-Dem-CPD-Party-V2.csv", show_col_types = FALSE)

likud <- df |>
  filter(country_text_id == "ISR",
         str_detect(v2paenname, "Likud")) |>
  select(year,
         v2paopresp, v2paopresp_codelow, v2paopresp_codehigh,
         v2paplur,   v2paplur_codelow,   v2paplur_codehigh,
         v2paminor,  v2paminor_codelow,  v2paminor_codehigh,
         v2paviol,   v2paviol_codelow,   v2paviol_codehigh) |>
  arrange(year)

# ── Reshape to long format ───────────────────────────────────────────────────
long <- likud |>
  pivot_longer(
    cols      = -year,
    names_to  = "variable",
    values_to = "value"
  ) |>
  mutate(
    component = case_when(
      str_detect(variable, "paopresp") ~ "Opponent Respect\nDemonisation of political rivals",
      str_detect(variable, "paplur")   ~ "Political Pluralism\nCommitment to elections & civil liberties",
      str_detect(variable, "paminor")  ~ "Minority Rights\nMajority override of minority rights",
      str_detect(variable, "paviol")   ~ "Rejection of Violence\nDiscourages political violence"
    ),
    type = case_when(
      str_ends(variable, "_codelow")  ~ "lo",
      str_ends(variable, "_codehigh") ~ "hi",
      TRUE                             ~ "est"
    )
  ) |>
  filter(!is.na(component)) |>
  pivot_wider(
    id_cols  = c(year, component),
    names_from  = type,
    values_from = value
  ) |>
  drop_na(est)

# Keep factor order
long <- long |>
  mutate(component = factor(component, levels = c(
    "Opponent Respect\nDemonisation of political rivals",
    "Political Pluralism\nCommitment to elections & civil liberties",
    "Minority Rights\nMajority override of minority rights",
    "Rejection of Violence\nDiscourages political violence"
  )))

panel_colors <- c(
  "Opponent Respect\nDemonisation of political rivals"                        = "#c0392b",
  "Political Pluralism\nCommitment to elections & civil liberties"            = "#2471a3",
  "Minority Rights\nMajority override of minority rights"                    = "#27ae60",
  "Rejection of Violence\nDiscourages political violence"                    = "#d4880e"
)

# ── Plot ─────────────────────────────────────────────────────────────────────
p <- ggplot(long, aes(x = year, y = est, colour = component, fill = component)) +
  geom_hline(yintercept = 0, linetype = "dashed", colour = "grey50", linewidth = 0.5) +
  geom_ribbon(aes(ymin = lo, ymax = hi), alpha = 0.15, colour = NA) +
  geom_line(linewidth = 1.0) +
  geom_point(size = 2.5) +
  scale_colour_manual(values = panel_colors, guide = "none") +
  scale_fill_manual(values = panel_colors,   guide = "none") +
  scale_x_continuous(breaks = seq(1975, 2020, by = 10)) +
  facet_wrap(~ component, ncol = 2, scales = "free_y") +
  labs(
    x       = "Election year",
    y       = "Latent score",
    caption = "95% CI shaded. Dashed line = 0 (global neutral). Source: V-Party v2."
  ) +
  theme_minimal(base_size = 11) +
  theme(
    strip.text       = element_text(face = "bold", hjust = 0, size = 10),
    panel.grid.minor = element_blank(),
    panel.grid.major.x = element_line(colour = "grey90"),
    axis.text.x      = element_text(angle = 30, hjust = 1),
    plot.caption     = element_text(colour = "grey50", size = 8, hjust = 0.5),
    plot.margin      = margin(10, 15, 5, 10)
  )

ggsave("israel_analysis_output/fig_apo_likud_clean.pdf",
       p, width = 13, height = 8, units = "in")
ggsave("israel_analysis_output/fig_apo_likud_clean_r.png",
       p, width = 13, height = 8, units = "in", dpi = 160)

message("Saved fig_apo_likud_clean.pdf and fig_apo_likud_clean_r.png")
