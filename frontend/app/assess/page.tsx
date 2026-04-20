"use client";

import { useRouter } from "next/navigation";
import AssessmentFlow from "@/app/components/AssessmentFlow";
import { FinalResult } from "@/app/lib/api";

export default function AssessPage() {
  const router = useRouter();

  const handleComplete = (result: FinalResult) => {
    sessionStorage.setItem("mindcompass_result", JSON.stringify(result));
    router.push("/result");
  };

  return <AssessmentFlow onComplete={handleComplete} />;
}