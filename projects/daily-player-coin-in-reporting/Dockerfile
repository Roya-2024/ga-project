FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN useradd --uid 10001 --create-home reporter && mkdir /app/reports /app/state && chown -R reporter:reporter /app
COPY --chown=reporter:reporter player_report /app/player_report
COPY --chown=reporter:reporter data /app/data
USER reporter
ENTRYPOINT ["python", "-m", "player_report"]
CMD ["--date", "2026-10-08"]
