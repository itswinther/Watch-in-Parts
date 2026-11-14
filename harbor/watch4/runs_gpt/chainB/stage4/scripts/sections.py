exec(open('/app/scripts/assemble.py').read().split('for n,s in solids.items():')[0])
for n in ['hour_hand','minute_hand','seconds_pinion','hour_wheel','upper_bridge','minute_input','reduction_input','lower_bridge']:
 print('\n',n)
 s=solids[n]
 for z in np.arange(s.bounding_box()[2]+.05,s.bounding_box()[5],.3):
  ps=s.slice(z).to_polygons()
  print(round(z,2),[(len(p),np.round(np.min(p,axis=0),3).tolist(),np.round(np.max(p,axis=0),3).tolist()) for p in ps])
