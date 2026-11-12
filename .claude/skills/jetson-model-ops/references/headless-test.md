# Headless load test for a model that does not fit beside the desktop

Write this as a script on the Jetson and start it detached (`setsid nohup ./try.sh >/dev/null 2>&1 </dev/null &`), then read its log. The restore runs even if the test fails.

```bash
#!/bin/bash
OUT=~/models/try.log; exec > $OUT 2>&1
MODEL=<ollama model name>
CONTAINER=<name of a container to stop and restart, for example anythingllm; leave empty if none>
restore() {
  ollama stop "$MODEL" 2>/dev/null
  sudo -n systemctl isolate graphical.target
  [ -n "$CONTAINER" ] && docker start "$CONTAINER" >/dev/null 2>&1
  sleep 15; docker ps --format '{{.Names}} {{.Status}}'; systemctl is-active ollama; free -m | sed -n 2p
  echo RESTORED > ~/models/try.done
}
trap restore EXIT
free -m | sed -n 2p
[ -n "$CONTAINER" ] && docker stop "$CONTAINER" >/dev/null 2>&1
sudo -n systemctl isolate multi-user.target; sleep 8
sudo -n systemctl start ollama          # isolate stopped it
for i in $(seq 1 30); do curl -s -o /dev/null http://127.0.0.1:11434/ && break; sleep 1; done
sync; echo 3 | sudo -n tee /proc/sys/vm/drop_caches >/dev/null
free -m | sed -n 2p
curl -s http://127.0.0.1:11434/api/generate -d "{\"model\":\"$MODEL\",\"prompt\":\"Reply with exactly: ok\",\"stream\":false,\"keep_alive\":0,\"options\":{\"num_ctx\":1024,\"num_batch\":128,\"num_predict\":48}}" > ~/models/resp.json
free -m | sed -n 2p
dmesg 2>/dev/null | tail -30 | grep -i -E 'oom|killed process' | tail -3
```

Read `load_duration`, `eval_count` and `eval_duration` from `resp.json` for load time and tokens/s. An OOM shows as `NvMapMemAllocInternalTagged failed` / 'killed by the OOM killer' in `journalctl -u ollama`, and the client sees `EOF`. Do not retry in a loop; recommend a smaller model.
