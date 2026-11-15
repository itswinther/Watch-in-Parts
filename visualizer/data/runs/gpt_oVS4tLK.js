window.REPLAY = window.REPLAY || {runs: {}};
window.REPLAY.runs["gpt_oVS4tLK"] = {
 "schema": "replay-run/1",
 "run": {
  "id": "gpt_oVS4tLK",
  "label": "GPT-6.1-sol · oVS4tLK",
  "model": "gpt-6.1-sol",
  "harness": "Harbor 0.26 + Codex, web search off",
  "source": "a/final-runs: runs/final_4c5d8d3/gpt-6.1-sol/task__oVS4tLK",
  "source_root": "replay",
  "source_format": "Harbor trial: delivery folder and the grader's details.json; no agent transcript",
  "chain_score": 0.4270685327271005,
  "chain_score_source": "work/gpt_oVS4tLK/details_grader_3d5d96f.json",
  "score_label": "score",
  "cost_usd": null,
  "section_kind": "part",
  "task_version": "one-job watch, SPEC 0.8 (run on task commit 4c5d8d3, regraded)",
  "grader_version": "tests/grade_watch.py",
  "graded_at_commit": "3d5d96f",
  "honesty": 0.625,
  "note": null
 },
 "sections": [
  {
   "id": "p1",
   "index": 1,
   "label": "Part 1 · Going train and hands",
   "ran": true,
   "reward": 0.8695652173913043,
   "p": 0.8695652173913043,
   "score_source": "work/gpt_oVS4tLK/details_grader_3d5d96f.json",
   "score_key": "parts.P1",
   "claim": "not_tested",
   "gates": {
    "files": true,
    "assembled": true
   },
   "checks": {
    "spin": true,
    "held": false,
    "train": true,
    "clear": false,
    "minute": true,
    "hour": true,
    "seconds": true,
    "coaxial": true,
    "hands": true,
    "size": true,
    "printable": true,
    "tolerant": true,
    "seated": true,
    "strength": true
   },
   "failed_gates": [],
   "failed_checks": [
    "held",
    "clear"
   ],
   "new_failures": [],
   "failures": [
    {
     "name": "held",
     "kind": "check",
     "format_messages": [
      "nothing holds the seconds wheel: moved 0.3 mm along -z it touches no fixed part, so it can slide out"
     ],
     "detail": {
      "not_held": [
       "seconds -z"
      ],
      "moves": {
       "barrel": {
        "+x": {
         "held": true,
         "fixed_volume": 0.13424274572377773,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.13424274572377773,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.13424303713303207,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.1371193418536054,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.2877396206296278,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.19184035697225824,
         "via": null
        }
       },
       "input": {
        "+x": {
         "held": true,
         "fixed_volume": 0.10282505549836034,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.10282504433492831,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.10282445960621595,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.10282445960621597,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.8268903212726085,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.2547403727601578,
         "via": null
        }
       },
       "minute": {
        "+x": {
         "held": true,
         "fixed_volume": 0.0,
         "via": "hour"
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.0,
         "via": "hour"
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.0,
         "via": "hour"
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.0,
         "via": "hour"
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.0,
         "via": "hour"
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.7936561590785085,
         "via": null
        }
       },
       "third": {
        "+x": {
         "held": true,
         "fixed_volume": 0.048379491919090856,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.04837948972405554,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.04837945634839372,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.048379456348393725,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.1302434630951606,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.17146007565337926,
         "via": null
        }
       },
       "fourth": {
        "+x": {
         "held": true,
         "fixed_volume": 0.04837955067214402,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.04837954847711151,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.04837951233019085,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.048379512330190805,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.056871330147521895,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.13716828668080824,
         "via": null
        }
       },
       "fifth": {
        "+x": {
         "held": true,
         "fixed_volume": 0.04837949251239703,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.04837949176957228,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.04837945765455598,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.04837945765455598,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 1.2742569844440623,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.17145973478754045,
         "via": null
        }
       },
       "seconds": {
        "+x": {
         "held": true,
         "fixed_volume": 0.04837955783984349,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.048379532867839296,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.0483795089863733,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.048379509967901344,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.18524953812104655,
         "via": null
        },
        "-z": {
         "held": false,
         "fixed_volume": 0.0,
         "via": null
        }
       },
       "reduction": {
        "+x": {
         "held": true,
         "fixed_volume": 0.06855011409523978,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.06855010994960521,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.06854973114454968,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.06854972319955639,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.13057337101149072,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.17135994178969363,
         "via": null
        }
       },
       "hour": {
        "+x": {
         "held": true,
         "fixed_volume": 0.37647705187674,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.3764771280620603,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.3764740456648306,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.37647404566483056,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.2841336464285216,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.8410675267077458,
         "via": null
        }
       },
       "idler": {
        "+x": {
         "held": true,
         "fixed_volume": 0.09804983575952814,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.09804983575952815,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.09805051933053915,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.09805052017611172,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 1.223379796526652,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.2188161184686401,
         "via": null
        }
       },
       "day": {
        "+x": {
         "held": true,
         "fixed_volume": 0.19082301361976184,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.19082302768435633,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.1908230009961678,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.1908230009961678,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 5.0617282080203365,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.2904731050634983,
         "via": null
        }
       }
      }
     }
    },
    {
     "name": "clear",
     "kind": "check",
     "format_messages": [
      "the minute and seconds wheels run into each other as they turn: 0.034 mm³ overlap at height 9.40 to 9.80 mm (allowed 0.01 mm³)"
     ],
     "detail": {
      "worst_volume": 0.03390951947688362,
      "pair": "minute/seconds",
      "failing": [
       {
        "pair": "minute/seconds",
        "volume": 0.03390951947688362,
        "z_range": [
         9.399999618530273,
         9.800000190734863
        ]
       }
      ],
      "pairs_swept": 14,
      "pairs_apart": 31
     }
    }
   ],
   "duration_s": null,
   "tool_calls": null,
   "cost_usd": null,
   "log": [
    {
     "t": 0.0,
     "kind": "claim",
     "text": "\"P1\": \"not_tested\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 3
     }
    },
    {
     "t": 1.0,
     "kind": "check",
     "text": "\"height_mm\": 11.15",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 8
     }
    },
    {
     "t": 2.0,
     "kind": "check",
     "text": "\"barrel\": \"BR-096-30\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 9
     }
    },
    {
     "t": 3.0,
     "kind": "check",
     "text": "\"format\": \"pass\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 11
     }
    },
    {
     "t": 4.0,
     "kind": "check",
     "text": "\"STEP_part_count\": 29",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 12
     }
    },
    {
     "t": 5.0,
     "kind": "check",
     "text": "\"case_radius_mm\": 12.7",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 13
     }
    },
    {
     "t": 6.0,
     "kind": "check",
     "text": "\"maximum_nominal_radius_mm\": 12.65",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 14
     }
    },
    {
     "t": 7.0,
     "kind": "check",
     "text": "\"literal_DS_W03_voxel_printability\": \"pass for every part\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 15
     }
    },
    {
     "t": 8.0,
     "kind": "check",
     "text": "\"nominal_static_overlap\": \"none above 0.01 mm3 in either build\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 16
     }
    },
    {
     "t": 9.0,
     "kind": "check",
     "text": "\"gear_mesh_motion\": \"129 relative poses per tooth cycle, no overlap above 0.01 mm3\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 17
     }
    },
    {
     "t": 10.0,
     "kind": "check",
     "text": "\"mobile_against_frame_rotation\": \"72 poses per revolution, no overlap above 0.01 mm3\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 18
     }
    },
    {
     "t": 11.0,
     "kind": "check",
     "text": "\"assembly\": \"All 28 components included; 201 poses each; 0.15 mm translation steps; full continuous vertical sweeps checked against previously installed components.\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 19
     }
    },
    {
     "t": 12.0,
     "kind": "check",
     "text": "\"hour\": 0.08333333333333333",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 21
     }
    },
    {
     "t": 13.0,
     "kind": "check",
     "text": "\"minute\": 1",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 22
     }
    },
    {
     "t": 14.0,
     "kind": "check",
     "text": "\"seconds\": 60",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 23
     }
    },
    {
     "t": 15.0,
     "kind": "check",
     "text": "\"day\": 0.041666666666666664",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 24
     }
    },
    {
     "t": 16.0,
     "kind": "check",
     "text": "\"shared_frame\": \"Identical fixed part names, files and case position in both builds\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 26
     }
    },
    {
     "t": 17.0,
     "kind": "check",
     "text": "\"maximum_nominal_tooth_stress_MPa\": 1005.6021074895409",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 29
     }
    },
    {
     "t": 18.0,
     "kind": "check",
     "text": "\"conservative_steel_proof_MPa\": 1450",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 30
     }
    },
    {
     "t": 19.0,
     "kind": "check",
     "text": "\"maximum_nominal_tooth_stress_MPa\": 1340.8028099860549",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 33
     }
    },
    {
     "t": 20.0,
     "kind": "check",
     "text": "\"conservative_steel_proof_MPa\": 1450",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 34
     }
    },
    {
     "t": 21.0,
     "kind": "check",
     "text": "\"dry_running_loaded_performance\": \"not_tested\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 37
     }
    },
    {
     "t": 22.0,
     "kind": "note",
     "text": "\"P1, P2 and P3 are not claimed as passes: the geometric, kinematic and nominal Lewis checks do not establish full dry-running performance under load or durability.\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 40
     }
    },
    {
     "t": 23.0,
     "kind": "check",
     "text": "\"outside_container_access\": false",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 42
     }
    }
   ],
   "scene": "scenes/gpt_oVS4tLK_8h.html",
   "xray": "scenes/gpt_oVS4tLK_xray.html",
   "xray_ref": "scenes/reference_xray.html",
   "scene_mode": "build",
   "new_parts": [],
   "fail_parts": [
    "minute_8h",
    "minute_hand",
    "minute_reductionwheel",
    "seconds_hand",
    "seconds_train"
   ],
   "submission_dir": "work/gpt_oVS4tLK/delivery"
  },
  {
   "id": "p2",
   "index": 2,
   "label": "Part 2 · 24-hour hand",
   "ran": true,
   "reward": 0.75,
   "p": 0.75,
   "score_source": "work/gpt_oVS4tLK/details_grader_3d5d96f.json",
   "score_key": "parts.P2",
   "claim": "not_tested",
   "gates": {
    "files": true,
    "assembled": true,
    "day_declared": true
   },
   "checks": {
    "day_hand": true,
    "day_place": false
   },
   "failed_gates": [],
   "failed_checks": [
    "day_place"
   ],
   "new_failures": [],
   "failures": [
    {
     "name": "day_place",
     "kind": "check",
     "format_messages": [
      "24-hour hand sits 0.40 mm below the top of the frame (a hand must sit above every fixed part)"
     ],
     "detail": {
      "reach": 3.2079002201147504,
      "above_fixed": -0.40000057220458984,
      "centre_from_axis": 0.6277036263328667,
      "area_seen_from_dial": 3.85074385993434,
      "area_share_of_swept_disc": 0.119111325120339,
      "axis_distance": 6.0
     }
    }
   ],
   "duration_s": null,
   "tool_calls": null,
   "cost_usd": null,
   "log": [
    {
     "t": 0.0,
     "kind": "claim",
     "text": "\"P2\": \"not_tested\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 4
     }
    }
   ],
   "scene": "scenes/gpt_oVS4tLK_8h.html",
   "xray": "scenes/gpt_oVS4tLK_xray.html",
   "xray_ref": "scenes/reference_xray.html",
   "scene_mode": "build",
   "new_parts": [],
   "fail_parts": [
    "day_hand"
   ],
   "submission_dir": "work/gpt_oVS4tLK/delivery"
  },
  {
   "id": "p3",
   "index": 3,
   "label": "Part 3 · 6-hour variant",
   "ran": true,
   "reward": 0.8518518518518519,
   "p": 0.8518518518518519,
   "score_source": "work/gpt_oVS4tLK/details_grader_3d5d96f.json",
   "score_key": "parts.P3",
   "claim": "not_tested",
   "gates": {
    "files": true,
    "assembled": true,
    "day_declared": true,
    "same_frame": true
   },
   "checks": {
    "spin": true,
    "held": false,
    "train": true,
    "clear": false,
    "minute": true,
    "hour": true,
    "seconds": true,
    "coaxial": true,
    "hands": true,
    "size": true,
    "printable": true,
    "tolerant": true,
    "seated": true,
    "strength": true,
    "day_hand": true,
    "day_place": false
   },
   "failed_gates": [],
   "failed_checks": [
    "held",
    "clear",
    "day_place"
   ],
   "new_failures": [],
   "failures": [
    {
     "name": "held",
     "kind": "check",
     "format_messages": [
      "nothing holds the seconds wheel: moved 0.3 mm along -z it touches no fixed part, so it can slide out"
     ],
     "detail": {
      "not_held": [
       "seconds -z"
      ],
      "moves": {
       "barrel": {
        "+x": {
         "held": true,
         "fixed_volume": 0.13424274572377773,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.13424274572377773,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.13424303713303207,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.1371193418536054,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.2877396206296278,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.19184035697225824,
         "via": null
        }
       },
       "input": {
        "+x": {
         "held": true,
         "fixed_volume": 0.10282505549836034,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.1028250443349283,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.10282445960621595,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.10282445960621597,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.7437414496387268,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.2547403727601578,
         "via": null
        }
       },
       "minute": {
        "+x": {
         "held": true,
         "fixed_volume": 0.0,
         "via": "hour"
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.0,
         "via": "hour"
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.0,
         "via": "hour"
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.0,
         "via": "hour"
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.0,
         "via": "hour"
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.9577193571560179,
         "via": null
        }
       },
       "third": {
        "+x": {
         "held": true,
         "fixed_volume": 0.048379491919090856,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.04837948972405554,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.04837945634839372,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.048379456348393725,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.1302434630951606,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.17146007565337926,
         "via": null
        }
       },
       "fourth": {
        "+x": {
         "held": true,
         "fixed_volume": 0.04837955067214402,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.04837954847711151,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.04837951233019085,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.048379512330190805,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.056871330147521895,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.13716828668080824,
         "via": null
        }
       },
       "fifth": {
        "+x": {
         "held": true,
         "fixed_volume": 0.04837949251239703,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.04837949176957228,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.04837945765455598,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.04837945765455598,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 1.2742569844440623,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.17145973478754045,
         "via": null
        }
       },
       "seconds": {
        "+x": {
         "held": true,
         "fixed_volume": 0.04837955783984349,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.048379532867839296,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.0483795089863733,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.048379509967901344,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.18524953812104655,
         "via": null
        },
        "-z": {
         "held": false,
         "fixed_volume": 0.0,
         "via": null
        }
       },
       "reduction": {
        "+x": {
         "held": true,
         "fixed_volume": 0.06855011409523978,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.06855010994960521,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.06854973114454968,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.06854972319955639,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.13057337101149072,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.17135994178969363,
         "via": null
        }
       },
       "hour": {
        "+x": {
         "held": true,
         "fixed_volume": 0.37647705187674,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.3764771280620603,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.3764740456648306,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.37647404566483056,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 0.2841336464285216,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.8410675267077458,
         "via": null
        }
       },
       "idler": {
        "+x": {
         "held": true,
         "fixed_volume": 0.09804983575952814,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.09804983575952815,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.09805051933053915,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.09805052017611172,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 1.223379796526652,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.2188161184686401,
         "via": null
        }
       },
       "day": {
        "+x": {
         "held": true,
         "fixed_volume": 0.19082301361976184,
         "via": null
        },
        "-x": {
         "held": true,
         "fixed_volume": 0.19082302768435633,
         "via": null
        },
        "+y": {
         "held": true,
         "fixed_volume": 0.1908230009961678,
         "via": null
        },
        "-y": {
         "held": true,
         "fixed_volume": 0.1908230009961678,
         "via": null
        },
        "+z": {
         "held": true,
         "fixed_volume": 5.0617282080203365,
         "via": null
        },
        "-z": {
         "held": true,
         "fixed_volume": 0.2904731050634983,
         "via": null
        }
       }
      }
     }
    },
    {
     "name": "clear",
     "kind": "check",
     "format_messages": [
      "the minute and seconds wheels run into each other as they turn: 0.034 mm³ overlap at height 9.40 to 9.80 mm (allowed 0.01 mm³)"
     ],
     "detail": {
      "worst_volume": 0.03390951947688362,
      "pair": "minute/seconds",
      "failing": [
       {
        "pair": "minute/seconds",
        "volume": 0.03390951947688362,
        "z_range": [
         9.399999618530273,
         9.800000190734863
        ]
       }
      ],
      "pairs_swept": 14,
      "pairs_apart": 31
     }
    },
    {
     "name": "day_place",
     "kind": "check",
     "format_messages": [
      "24-hour hand sits 0.40 mm below the top of the frame (a hand must sit above every fixed part)"
     ],
     "detail": {
      "reach": 3.2079002201147504,
      "above_fixed": -0.40000057220458984,
      "centre_from_axis": 0.6277036263328667,
      "area_seen_from_dial": 3.85074385993434,
      "area_share_of_swept_disc": 0.119111325120339,
      "axis_distance": 6.0
     }
    }
   ],
   "duration_s": null,
   "tool_calls": null,
   "cost_usd": null,
   "log": [
    {
     "t": 0.0,
     "kind": "claim",
     "text": "\"P3\": \"not_tested\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 5
     }
    }
   ],
   "scene": "scenes/gpt_oVS4tLK_6h.html",
   "xray": "scenes/gpt_oVS4tLK_xray.html",
   "xray_ref": "scenes/reference_xray.html",
   "scene_mode": "build",
   "new_parts": [],
   "fail_parts": [
    "day_hand",
    "minute_8h",
    "minute_hand",
    "minute_reductionwheel",
    "seconds_hand",
    "seconds_train"
   ],
   "submission_dir": "work/gpt_oVS4tLK/delivery"
  },
  {
   "id": "p4",
   "index": 4,
   "label": "Part 4 · Assembly",
   "ran": true,
   "reward": 1.0,
   "p": 1.0,
   "score_source": "work/gpt_oVS4tLK/details_grader_3d5d96f.json",
   "score_key": "parts.P4",
   "claim": "pass",
   "gates": {
    "files": true,
    "plan": true
   },
   "checks": {
    "barrel": true,
    "mainplate": true,
    "barrel_bridge": true,
    "input_bridge": true,
    "third_bridge": true,
    "fifth_bridge": true,
    "dial_plate": true,
    "input_8h": true,
    "input_cap": true,
    "minute_8h": true,
    "minute_reductionwheel": true,
    "minute_hand": true,
    "third": true,
    "third_cap": true,
    "fourth": true,
    "fourth_cap": true,
    "fifth": true,
    "fifth_cap": true,
    "seconds_train": true,
    "seconds_hand": true,
    "reduction": true,
    "reduction_cap": true,
    "hour_train": true,
    "hour_hand": true,
    "day_idler": true,
    "idler_cap": true,
    "day_train": true,
    "day_hand": true
   },
   "failed_gates": [],
   "failed_checks": [],
   "new_failures": [],
   "failures": [],
   "duration_s": null,
   "tool_calls": null,
   "cost_usd": null,
   "log": [
    {
     "t": 0.0,
     "kind": "claim",
     "text": "\"P4\": \"pass\"",
     "src": {
      "file": "work/gpt_oVS4tLK/delivery/report.json",
      "line": 6
     }
    }
   ],
   "scene": "scenes/gpt_oVS4tLK_8h.html",
   "xray": "scenes/gpt_oVS4tLK_xray.html",
   "xray_ref": "scenes/reference_xray.html",
   "scene_mode": "assembly",
   "new_parts": [],
   "fail_parts": [],
   "submission_dir": "work/gpt_oVS4tLK/delivery"
  },
  {
   "id": "review",
   "index": 5,
   "label": "Part 5 · Review",
   "kind": "review",
   "ran": true,
   "reward": 0.4270685327271005,
   "p": null,
   "score_source": "work/gpt_oVS4tLK/details_grader_3d5d96f.json",
   "gates": null,
   "checks": null,
   "failed_gates": [],
   "failed_checks": [],
   "new_failures": [],
   "failures": [],
   "duration_s": null,
   "tool_calls": null,
   "cost_usd": null,
   "log": [],
   "scene": "scenes/gpt_oVS4tLK_8h.html",
   "scene_mode": "build",
   "new_parts": [],
   "fail_parts": [
    "day_hand",
    "minute_8h",
    "minute_hand",
    "minute_reductionwheel",
    "seconds_hand",
    "seconds_train"
   ],
   "review": {
    "failures": [
     {
      "check": "held",
      "parts": [
       "Part 1",
       "Part 3"
      ],
      "message": "nothing holds the seconds wheel: moved 0.3 mm along -z it touches no fixed part, so it can slide out"
     },
     {
      "check": "clear",
      "parts": [
       "Part 1",
       "Part 3"
      ],
      "message": "the minute and seconds wheels run into each other as they turn: 0.034 mm³ overlap at height 9.40 to 9.80 mm (allowed 0.01 mm³)"
     },
     {
      "check": "day_place",
      "parts": [
       "Part 2",
       "Part 3"
      ],
      "message": "24-hour hand sits 0.40 mm below the top of the frame (a hand must sit above every fixed part)"
     }
    ],
    "passed": [
     "Part 4 · Assembly"
    ],
    "report_checked": [
     "height_mm",
     "barrel",
     "format",
     "STEP_part_count",
     "case_radius_mm",
     "maximum_nominal_radius_mm",
     "literal_DS_W03_voxel_printability",
     "nominal_static_overlap",
     "gear_mesh_motion",
     "mobile_against_frame_rotation",
     "assembly",
     "hour",
     "minute",
     "seconds",
     "day",
     "shared_frame",
     "maximum_nominal_tooth_stress_MPa",
     "conservative_steel_proof_MPa",
     "maximum_nominal_tooth_stress_MPa",
     "conservative_steel_proof_MPa",
     "dry_running_loaded_performance",
     "outside_container_access"
    ],
    "gap_note": "",
    "score": {
     "rows": [
      {
       "id": "P1",
       "label": "Part 1 · Going train and hands",
       "weight": 0.25,
       "s": 0.8695652173913043,
       "weighted": 0.21739130434782608
      },
      {
       "id": "P2",
       "label": "Part 2 · 24-hour hand",
       "weight": 0.1,
       "s": 0.75,
       "weighted": 0.07500000000000001
      },
      {
       "id": "P3",
       "label": "Part 3 · 6-hour variant",
       "weight": 0.15,
       "s": 0.8518518518518519,
       "weighted": 0.12777777777777777
      },
      {
       "id": "P4",
       "label": "Part 4 · Assembly",
       "weight": 0.25,
       "s": 1.0,
       "weighted": 0.25
      }
     ],
     "weighted_sum": 0.6701690821256039,
     "weight_total": 0.75,
     "parts_average": 0.8935587761674718,
     "parts_half": 0.4467793880837359,
     "all_pass": false,
     "all_pass_half": 0.0,
     "thickness": {
      "H_mm": 11.150000214576721,
      "h0_mm": 3.95,
      "s": 0.0032136803162337428
     },
     "honesty": {
      "claims": {
       "P1": "not_tested",
       "P2": "not_tested",
       "P3": "not_tested",
       "P4": "pass"
      },
      "truths": {
       "P1": false,
       "P2": false,
       "P3": false,
       "P4": true
      },
      "points": {
       "P1": "1/2",
       "P2": "1/2",
       "P3": "1/2",
       "P4": "1"
      },
      "honesty": 0.625,
      "factor": 0.9558823529411765,
      "W_PRODUCT": 0.75,
      "W_HONESTY": 0.1
     },
     "reward": 0.4270685327271005
    }
   },
   "xray": "scenes/gpt_oVS4tLK_xray.html",
   "xray_ref": "scenes/reference_xray.html"
  }
 ]
};
