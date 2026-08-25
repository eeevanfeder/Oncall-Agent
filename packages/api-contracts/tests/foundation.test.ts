import { describe, expect, it } from "vitest";

import { FOUNDATION_CONTRACT_VERSION, type HealthData } from "../src/index";

describe("foundation contracts", () => {
  it("导出最小 health data 与合同版本", () => {
    const sample: HealthData = { status: "ok" };
    expect(sample.status).toBe("ok");
    expect(FOUNDATION_CONTRACT_VERSION).toBe("0.2.0");
  });
});
