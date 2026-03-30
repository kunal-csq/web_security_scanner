import { createBrowserRouter } from "react-router-dom";

import { LandingPage } from "./pages/LandingPage";
import { ScanSetup } from "./pages/ScanSetup";
import { ScanProgress } from "./pages/ScanProgress";
import { ScanResults } from "./pages/ScanResults";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage />,
  },
  {
    path: "/scan",
    element: <ScanSetup />,
  },
  {
    path: "/scanning",
    element: <ScanProgress />,
  },
  {
    path: "/results",
    element: <ScanResults />,
  },
]);
