window.REPLAY = window.REPLAY || {runs: {}};
window.REPLAY.runs["gpt_owFDECg"] = {
 "schema": "replay-run/1",
 "run": {
  "id": "gpt_owFDECg",
  "label": "GPT-6.1-sol · owFDECg",
  "model": "gpt-6.1-sol",
  "harness": "Harbor 0.26 + Codex, web search off",
  "source": "a/final-runs: runs/final_3d5d96f/gpt-6.1-sol/task__owFDECg",
  "source_root": "replay",
  "source_format": "Harbor trial: delivery folder and the grader's details.json; no agent transcript",
  "chain_score": 0.4270685327271005,
  "chain_score_source": "work/gpt_owFDECg/details.json",
  "score_label": "score",
  "cost_usd": null,
  "section_kind": "part",
  "task_version": "one-job watch, SPEC 0.8",
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
   "score_source": "work/gpt_owFDECg/details.json",
   "score_key": "parts.P1",
   "claim": "not_tested",
   "gates": {
    "files": true,
    "assembled": true
   },
   "checks": {
    "spin": true,
    "held": true,
    "train": true,
    "clear": true,
    "minute": true,
    "hour": true,
    "seconds": true,
    "coaxial": true,
    "hands": false,
    "size": true,
    "printable": true,
    "tolerant": true,
    "seated": false,
    "strength": true
   },
   "failed_gates": [],
   "failed_checks": [
    "hands",
    "seated"
   ],
   "new_failures": [],
   "failures": [
    {
     "name": "hands",
     "kind": "check",
     "format_messages": [
      "hour hand sits 0.25 mm below the top of the frame (a hand must sit above every fixed part); seconds hand sits 0.60 mm below the top of the frame (a hand must sit above every fixed part)"
     ],
     "detail": {
      "hour": {
       "reach": 5.50460035269731,
       "above_fixed": -0.25,
       "centre_from_axis": 1.3098530509960151,
       "area_seen_from_dial": 4.862552187558393,
       "area_share_of_swept_disc": 0.05108140281569367
      },
      "minute": {
       "reach": 6.004217458265164,
       "above_fixed": 0.10000038146972656,
       "centre_from_axis": 1.5482491316160374,
       "area_seen_from_dial": 5.058397465596625,
       "area_share_of_swept_disc": 0.04466324285474055
      },
      "seconds": {
       "reach": 5.005060125955865,
       "above_fixed": -0.6000003814697266,
       "centre_from_axis": 1.2658818564369378,
       "area_seen_from_dial": 4.2315618866262525,
       "area_share_of_swept_disc": 0.0537690329986933
      }
     }
    },
    {
     "name": "seated",
     "kind": "check",
     "format_messages": [
      "not seated on the rest of their wheel: A_lower, A_upper, hour_idle_lower, hour_idle_upper"
     ],
     "detail": {
      "not_seated": [
       "A_lower",
       "A_upper",
       "hour_idle_lower",
       "hour_idle_upper"
      ],
      "not_in_one_piece": [],
      "pieces": {
       "transfer": [
        [
         "transfer_lower",
         "transfer_8"
        ]
       ],
       "minute": [
        [
         "minute_lower_8",
         "minute_upper",
         "minute_hand"
        ]
       ],
       "hour": [
        [
         "hour_wheel",
         "hour_hand"
        ]
       ],
       "hour_idle": [
        [
         "hour_idle_lower",
         "hour_idle_upper"
        ]
       ],
       "A": [
        [
         "A_lower",
         "A_upper"
        ]
       ],
       "seconds": [
        [
         "seconds_wheel",
         "seconds_hand"
        ]
       ],
       "day": [
        [
         "day_wheel",
         "day_hand"
        ]
       ]
      },
      "moves": {
       "transfer": {
        "transfer_lower": {
         "+x": 0.021709608928889373,
         "-x": 0.02170959821409122,
         "+y": 0.02170954612372516,
         "-y": 0.021709546123725162,
         "+z": 0.05652525065781747,
         "-z": 0.0
        },
        "transfer_8": {
         "+x": 0.021709598214091224,
         "-x": 0.021709608928889366,
         "+y": 0.021709546123725162,
         "-y": 0.02170954612372516,
         "+z": 0.0,
         "-z": 0.0565252506578175
        }
       },
       "minute": {
        "minute_lower_8": {
         "+x": 0.05513494836617403,
         "-x": 0.0551349470049296,
         "+y": 0.05513424629154917,
         "-y": 0.05513424629154918,
         "+z": 0.6228662259723435,
         "-z": 0.0
        },
        "minute_upper": {
         "+x": 0.13854615699996384,
         "-x": 0.1385461540588627,
         "+y": 0.1385447968119303,
         "-y": 0.13854479681193033,
         "+z": 0.11305019026132647,
         "-z": 0.6228662259723439
        },
        "minute_hand": {
         "+x": 0.08341120569268862,
         "-x": 0.08341120999503428,
         "+y": 0.08341055052038113,
         "-y": 0.08341055052038111,
         "+z": 0.0,
         "-z": 0.11305019026132646
        }
       },
       "hour": {
        "hour_wheel": {
         "+x": 0.179285249763203,
         "-x": 0.17928524976320315,
         "+y": 0.17928457849460855,
         "-y": 0.17928457849460847,
         "+z": 0.41451837581281303,
         "-z": 0.0
        },
        "hour_hand": {
         "+x": 0.17928524976320304,
         "-x": 0.17928524976320306,
         "+y": 0.17928457849460844,
         "-y": 0.17928457849460847,
         "+z": 0.0,
         "-z": 0.41451841099000747
        }
       },
       "hour_idle": {
        "hour_idle_lower": {
         "+x": 0.007138782473152823,
         "-x": 0.007138782450629718,
         "+y": 0.007138123139401761,
         "-y": 0.007138126443032976,
         "+z": 0.24494268500867505,
         "-z": 0.0
        },
        "hour_idle_upper": {
         "+x": 0.007138782450629714,
         "-x": 0.0071387824731528335,
         "+y": 0.007138126443032973,
         "-y": 0.007138123139401758,
         "+z": 0.0,
         "-z": 0.24494268500867505
        }
       },
       "A": {
        "A_lower": {
         "+x": 0.005573032221002704,
         "-x": 0.00557303199049247,
         "+y": 0.0055734667211985705,
         "-y": 0.005573466721198567,
         "+z": 0.18841744018927398,
         "-z": 0.0
        },
        "A_upper": {
         "+x": 0.005573031990492467,
         "-x": 0.005573032221002701,
         "+y": 0.005573466721198572,
         "-y": 0.005573466721198569,
         "+z": 0.0,
         "-z": 0.188417440189274
        }
       },
       "B": {},
       "C": {},
       "day_idle": {},
       "seconds": {
        "seconds_wheel": {
         "+x": 0.1100280771959957,
         "-x": 0.1100280901401122,
         "+y": 0.11002764942707231,
         "-y": 0.11002764942707238,
         "+z": 0.20490395017203625,
         "-z": 0.0
        },
        "seconds_hand": {
         "+x": 0.11002809014011213,
         "-x": 0.11002807719599575,
         "+y": 0.1100276494270724,
         "-y": 0.11002764942707237,
         "+z": 0.0,
         "-z": 0.20490396772498268
        }
       },
       "day": {
        "day_wheel": {
         "+x": 0.11002807719599574,
         "-x": 0.11002809014011217,
         "+y": 0.11002764942707247,
         "-y": 0.1100276494270724,
         "+z": 0.2049039501720363,
         "-z": 0.0
        },
        "day_hand": {
         "+x": 0.11002809014011214,
         "-x": 0.11002807719599572,
         "+y": 0.11002764942707235,
         "-y": 0.11002764942707234,
         "+z": 0.0,
         "-z": 0.2049039690203553
        }
       }
      }
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
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 3
     }
    },
    {
     "t": 1.0,
     "kind": "check",
     "text": "\"height_mm\": 10.05",
     "src": {
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 8
     }
    },
    {
     "t": 2.0,
     "kind": "check",
     "text": "\"format\": \"pass\"",
     "src": {
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 10
     }
    },
    {
     "t": 3.0,
     "kind": "check",
     "text": "\"print_feature_voxels\": \"pass for all 35 referenced STEP parts\"",
     "src": {
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 11
     }
    },
    {
     "t": 4.0,
     "kind": "check",
     "text": "\"nominal_assembled_interference\": \"pass\"",
     "src": {
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 12
     }
    },
    {
     "t": 5.0,
     "kind": "check",
     "text": "\"hand_rates_both_builds\": \"hour 1/12 rph, minute 1 rph, seconds 60 rph, day 1/24 rph; all clockwise\"",
     "src": {
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 13
     }
    },
    {
     "t": 6.0,
     "kind": "check",
     "text": "\"running_clearance_samples\": \"61 coherent poses per build across 24 hours; no pair intersection above 0.01 mm3\"",
     "src": {
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 14
     }
    },
    {
     "t": 7.0,
     "kind": "check",
     "text": "\"assembly_clearance\": \"All vertical-prism height breakpoints checked against already installed parts; no intersection above 0.01 mm3\"",
     "src": {
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 15
     }
    },
    {
     "t": 8.0,
     "kind": "note",
     "text": "\"Complete dry-running friction and torque budget\"",
     "src": {
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 18
     }
    },
    {
     "t": 9.0,
     "kind": "note",
     "text": "\"Worst-case printing tolerance and loaded bearing displacement\"",
     "src": {
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 19
     }
    },
    {
     "t": 10.0,
     "kind": "note",
     "text": "\"Proof of minimum possible height\"",
     "src": {
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 20
     }
    },
    {
     "t": 11.0,
     "kind": "check",
     "text": "\"external_access\": \"None; all work remained inside this container.\"",
     "src": {
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 22
     }
    }
   ],
   "scene": "scenes/gpt_owFDECg_8h.html",
   "xray": "scenes/gpt_owFDECg_xray.html",
   "xray_ref": "scenes/reference_xray.html",
   "scene_mode": "build",
   "new_parts": [],
   "fail_parts": [
    "A_lower",
    "A_upper",
    "hour_hand",
    "hour_idle_lower",
    "hour_idle_upper",
    "seconds_hand"
   ],
   "submission_dir": "work/gpt_owFDECg/delivery"
  },
  {
   "id": "p2",
   "index": 2,
   "label": "Part 2 · 24-hour hand",
   "ran": true,
   "reward": 0.75,
   "p": 0.75,
   "score_source": "work/gpt_owFDECg/details.json",
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
      "24-hour hand sits 0.60 mm below the top of the frame (a hand must sit above every fixed part)"
     ],
     "detail": {
      "reach": 3.2079002201147504,
      "above_fixed": -0.6000003814697266,
      "centre_from_axis": 0.5949501489609251,
      "area_seen_from_dial": 3.421562447334793,
      "area_share_of_swept_disc": 0.10583587273212883,
      "axis_distance": 7.0
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
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 4
     }
    }
   ],
   "scene": "scenes/gpt_owFDECg_8h.html",
   "xray": "scenes/gpt_owFDECg_xray.html",
   "xray_ref": "scenes/reference_xray.html",
   "scene_mode": "build",
   "new_parts": [],
   "fail_parts": [
    "day_hand"
   ],
   "submission_dir": "work/gpt_owFDECg/delivery"
  },
  {
   "id": "p3",
   "index": 3,
   "label": "Part 3 · 6-hour variant",
   "ran": true,
   "reward": 0.8518518518518519,
   "p": 0.8518518518518519,
   "score_source": "work/gpt_owFDECg/details.json",
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
    "held": true,
    "train": true,
    "clear": true,
    "minute": true,
    "hour": true,
    "seconds": true,
    "coaxial": true,
    "hands": false,
    "size": true,
    "printable": true,
    "tolerant": true,
    "seated": false,
    "strength": true,
    "day_hand": true,
    "day_place": false
   },
   "failed_gates": [],
   "failed_checks": [
    "hands",
    "seated",
    "day_place"
   ],
   "new_failures": [],
   "failures": [
    {
     "name": "hands",
     "kind": "check",
     "format_messages": [
      "hour hand sits 0.25 mm below the top of the frame (a hand must sit above every fixed part); seconds hand sits 0.60 mm below the top of the frame (a hand must sit above every fixed part)"
     ],
     "detail": {
      "hour": {
       "reach": 5.50460035269731,
       "above_fixed": -0.25,
       "centre_from_axis": 1.3098530509960151,
       "area_seen_from_dial": 4.862552187558393,
       "area_share_of_swept_disc": 0.05108140281569367
      },
      "minute": {
       "reach": 6.004217458265164,
       "above_fixed": 0.10000038146972656,
       "centre_from_axis": 1.5482491316160374,
       "area_seen_from_dial": 5.058397465596625,
       "area_share_of_swept_disc": 0.04466324285474055
      },
      "seconds": {
       "reach": 5.005060125955865,
       "above_fixed": -0.6000003814697266,
       "centre_from_axis": 1.2658818564369378,
       "area_seen_from_dial": 4.2315618866262525,
       "area_share_of_swept_disc": 0.0537690329986933
      }
     }
    },
    {
     "name": "seated",
     "kind": "check",
     "format_messages": [
      "not seated on the rest of their wheel: A_lower, A_upper, hour_idle_lower, hour_idle_upper"
     ],
     "detail": {
      "not_seated": [
       "A_lower",
       "A_upper",
       "hour_idle_lower",
       "hour_idle_upper"
      ],
      "not_in_one_piece": [],
      "pieces": {
       "transfer": [
        [
         "transfer_lower",
         "transfer_6"
        ]
       ],
       "minute": [
        [
         "minute_lower_6",
         "minute_upper",
         "minute_hand"
        ]
       ],
       "hour": [
        [
         "hour_wheel",
         "hour_hand"
        ]
       ],
       "hour_idle": [
        [
         "hour_idle_lower",
         "hour_idle_upper"
        ]
       ],
       "A": [
        [
         "A_lower",
         "A_upper"
        ]
       ],
       "seconds": [
        [
         "seconds_wheel",
         "seconds_hand"
        ]
       ],
       "day": [
        [
         "day_wheel",
         "day_hand"
        ]
       ]
      },
      "moves": {
       "transfer": {
        "transfer_lower": {
         "+x": 0.021709608928889377,
         "-x": 0.021709598214091224,
         "+y": 0.021709546123725162,
         "-y": 0.02170954612372516,
         "+z": 0.056525250657817466,
         "-z": 0.0
        },
        "transfer_6": {
         "+x": 0.021709598214091227,
         "-x": 0.021709608928889373,
         "+y": 0.021709546123725162,
         "-y": 0.021709546123725155,
         "+z": 0.0,
         "-z": 0.056525250657817494
        }
       },
       "minute": {
        "minute_lower_6": {
         "+x": 0.05513494836617403,
         "-x": 0.05513494700492961,
         "+y": 0.05513424629154917,
         "-y": 0.05513424629154918,
         "+z": 0.6228662259723438,
         "-z": 0.0
        },
        "minute_upper": {
         "+x": 0.13854615699996384,
         "-x": 0.1385461540588627,
         "+y": 0.1385447968119303,
         "-y": 0.13854479681193033,
         "+z": 0.11305019026132647,
         "-z": 0.6228662259723441
        },
        "minute_hand": {
         "+x": 0.08341120569268862,
         "-x": 0.08341120999503428,
         "+y": 0.08341055052038113,
         "-y": 0.08341055052038111,
         "+z": 0.0,
         "-z": 0.11305019026132646
        }
       },
       "hour": {
        "hour_wheel": {
         "+x": 0.179285249763203,
         "-x": 0.17928524976320315,
         "+y": 0.17928457849460855,
         "-y": 0.17928457849460847,
         "+z": 0.41451837581281303,
         "-z": 0.0
        },
        "hour_hand": {
         "+x": 0.17928524976320304,
         "-x": 0.17928524976320306,
         "+y": 0.17928457849460844,
         "-y": 0.17928457849460847,
         "+z": 0.0,
         "-z": 0.41451841099000747
        }
       },
       "hour_idle": {
        "hour_idle_lower": {
         "+x": 0.007138782473152823,
         "-x": 0.007138782450629718,
         "+y": 0.007138123139401761,
         "-y": 0.007138126443032976,
         "+z": 0.24494268500867505,
         "-z": 0.0
        },
        "hour_idle_upper": {
         "+x": 0.007138782450629714,
         "-x": 0.0071387824731528335,
         "+y": 0.007138126443032973,
         "-y": 0.007138123139401758,
         "+z": 0.0,
         "-z": 0.24494268500867505
        }
       },
       "A": {
        "A_lower": {
         "+x": 0.005573032221002704,
         "-x": 0.00557303199049247,
         "+y": 0.0055734667211985705,
         "-y": 0.005573466721198567,
         "+z": 0.18841744018927398,
         "-z": 0.0
        },
        "A_upper": {
         "+x": 0.005573031990492467,
         "-x": 0.005573032221002701,
         "+y": 0.005573466721198572,
         "-y": 0.005573466721198569,
         "+z": 0.0,
         "-z": 0.188417440189274
        }
       },
       "B": {},
       "C": {},
       "day_idle": {},
       "seconds": {
        "seconds_wheel": {
         "+x": 0.1100280771959957,
         "-x": 0.1100280901401122,
         "+y": 0.11002764942707231,
         "-y": 0.11002764942707238,
         "+z": 0.20490395017203625,
         "-z": 0.0
        },
        "seconds_hand": {
         "+x": 0.11002809014011213,
         "-x": 0.11002807719599575,
         "+y": 0.1100276494270724,
         "-y": 0.11002764942707237,
         "+z": 0.0,
         "-z": 0.20490396772498268
        }
       },
       "day": {
        "day_wheel": {
         "+x": 0.11002807719599574,
         "-x": 0.11002809014011217,
         "+y": 0.11002764942707247,
         "-y": 0.1100276494270724,
         "+z": 0.2049039501720363,
         "-z": 0.0
        },
        "day_hand": {
         "+x": 0.11002809014011214,
         "-x": 0.11002807719599572,
         "+y": 0.11002764942707235,
         "-y": 0.11002764942707234,
         "+z": 0.0,
         "-z": 0.2049039690203553
        }
       }
      }
     }
    },
    {
     "name": "day_place",
     "kind": "check",
     "format_messages": [
      "24-hour hand sits 0.60 mm below the top of the frame (a hand must sit above every fixed part)"
     ],
     "detail": {
      "reach": 3.2079002201147504,
      "above_fixed": -0.6000003814697266,
      "centre_from_axis": 0.5949501489609251,
      "area_seen_from_dial": 3.421562447334793,
      "area_share_of_swept_disc": 0.10583587273212883,
      "axis_distance": 7.0
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
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 5
     }
    }
   ],
   "scene": "scenes/gpt_owFDECg_6h.html",
   "xray": "scenes/gpt_owFDECg_xray.html",
   "xray_ref": "scenes/reference_xray.html",
   "scene_mode": "build",
   "new_parts": [],
   "fail_parts": [
    "A_lower",
    "A_upper",
    "day_hand",
    "hour_hand",
    "hour_idle_lower",
    "hour_idle_upper",
    "seconds_hand"
   ],
   "submission_dir": "work/gpt_owFDECg/delivery"
  },
  {
   "id": "p4",
   "index": 4,
   "label": "Part 4 · Assembly",
   "ran": true,
   "reward": 1.0,
   "p": 1.0,
   "score_source": "work/gpt_owFDECg/details.json",
   "score_key": "parts.P4",
   "claim": "pass",
   "gates": {
    "files": true,
    "plan": true
   },
   "checks": {
    "barrel": true,
    "lower_frame": true,
    "centre_bridge": true,
    "upper_frame": true,
    "hour_idle_post": true,
    "hour_idle_bridge": true,
    "transfer_bridge": true,
    "B_bracket": true,
    "C_bracket": true,
    "seconds_bracket": true,
    "day_idle_bracket": true,
    "A_keeper": true,
    "B_keeper": true,
    "C_keeper": true,
    "day_idle_keeper": true,
    "dial": true,
    "transfer_lower": true,
    "transfer_8": true,
    "minute_lower_8": true,
    "minute_upper": true,
    "minute_hand": true,
    "hour_wheel": true,
    "hour_hand": true,
    "hour_idle_lower": true,
    "hour_idle_upper": true,
    "A_lower": true,
    "A_upper": true,
    "B_wheel": true,
    "C_wheel": true,
    "day_idle_wheel": true,
    "seconds_wheel": true,
    "seconds_hand": true,
    "day_wheel": true,
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
      "file": "work/gpt_owFDECg/delivery/report.json",
      "line": 6
     }
    }
   ],
   "scene": "scenes/gpt_owFDECg_8h.html",
   "xray": "scenes/gpt_owFDECg_xray.html",
   "xray_ref": "scenes/reference_xray.html",
   "scene_mode": "assembly",
   "new_parts": [],
   "fail_parts": [],
   "submission_dir": "work/gpt_owFDECg/delivery"
  },
  {
   "id": "review",
   "index": 5,
   "label": "Part 5 · Review",
   "kind": "review",
   "ran": true,
   "reward": 0.4270685327271005,
   "p": null,
   "score_source": "work/gpt_owFDECg/details.json",
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
   "scene": "scenes/gpt_owFDECg_8h.html",
   "scene_mode": "build",
   "new_parts": [],
   "fail_parts": [
    "A_lower",
    "A_upper",
    "day_hand",
    "hour_hand",
    "hour_idle_lower",
    "hour_idle_upper",
    "seconds_hand"
   ],
   "review": {
    "failures": [
     {
      "check": "hands",
      "parts": [
       "Part 1",
       "Part 3"
      ],
      "message": "hour hand sits 0.25 mm below the top of the frame (a hand must sit above every fixed part); seconds hand sits 0.60 mm below the top of the frame (a hand must sit above every fixed part)"
     },
     {
      "check": "seated",
      "parts": [
       "Part 1",
       "Part 3"
      ],
      "message": "not seated on the rest of their wheel: A_lower, A_upper, hour_idle_lower, hour_idle_upper"
     },
     {
      "check": "day_place",
      "parts": [
       "Part 2",
       "Part 3"
      ],
      "message": "24-hour hand sits 0.60 mm below the top of the frame (a hand must sit above every fixed part)"
     }
    ],
    "passed": [
     "Part 4 · Assembly"
    ],
    "report_checked": [
     "height_mm",
     "format",
     "print_feature_voxels",
     "nominal_assembled_interference",
     "hand_rates_both_builds",
     "running_clearance_samples",
     "assembly_clearance",
     "external_access"
    ],
    "gap_note": "None of the checks in its report looks at how high the hands sit or whether a wheel's pieces are seated on each other, which is where the grader failed it.",
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
      "H_mm": 10.049999594688416,
      "h0_mm": 3.95,
      "s": 0.01579254795353814
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
   "xray": "scenes/gpt_owFDECg_xray.html",
   "xray_ref": "scenes/reference_xray.html"
  }
 ]
};
