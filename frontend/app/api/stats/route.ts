import { NextResponse } from "next/server";
import { execFile } from "child_process";

export async function GET() {
  return new Promise((resolve) => {
    const pythonCode = `
import sys
sys.path.insert(0, r"C:\\Users\\khush\\murf-livekit-starter\\backend")
from memory import get_call_stats
import json
print(json.dumps(get_call_stats()))
`;

    execFile(
      "python",
      ["-c", pythonCode],
      { windowsHide: true },
      (error, stdout, stderr) => {
        if (error) {
          console.error(stderr || error.message);

          resolve(
            NextResponse.json(
              { error: "Unable to read call statistics" },
              { status: 500 }
            )
          );

          return;
        }

        try {
          const stats = JSON.parse(stdout.trim());

          resolve(
            NextResponse.json(stats)
          );
        } catch {
          resolve(
            NextResponse.json(
              { error: "Invalid statistics response" },
              { status: 500 }
            )
          );
        }
      }
    );
  });
}