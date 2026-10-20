import json, math
DIMS = {
 'A-11': dict(n=13.16, s=11.16, d=17.16, kind='trap'),
 'A-12': dict(n=10.00, s=11.00, d=16.90, kind='trap'),
 'A-13': dict(n=10.00, s=11.00, d=16.33, kind='trap'),
 'A-14': dict(n=9.23,  s=14.24, d=13.66, kind='irr'),
 'A-21': dict(n=11.16, s=11.16, d=15.00, kind='irr'),
 'A-22': dict(n=11.00, s=11.00, d=15.00, kind='trap'),
 'A-23': dict(n=11.00, s=11.00, d=15.00, kind='trap'),
 'A-24': dict(n=14.24, s=14.24, d=15.00, kind='irr'),
 'B-11': dict(n=19.75, s=None,  d=16.41, kind='irr'),
 'B-12': dict(n=10.00, s=None,  d=21.27, kind='irr'),
 'B-13': dict(n=10.00, s=None,  d=26.13, kind='irr'),
 'B-14': dict(n=8.82,  s=20.80, d=20.00, kind='trap'),
 'B-15': dict(n=20.80, s=None,  d=None,  kind='irr'),
}
LAB = {'A-11':173.92,'A-12':171.26,'A-13':166.16,'A-14':178.45,'A-21':211.15,'A-22':165.00,
       'A-23':165.00,'A-24':193.04,'B-11':215.51,'B-12':188.42,'B-13':237.04,'B-14':296.31,'B-15':334.42}
out={}
for k,v in DIMS.items():
    if v['kind']=='trap' and v['s']:
        d=(v['n']+v['s'])/2*v['d']
        out[k]=dict(calc=round(d,2), label=LAB[k], dev=round((LAB[k]-d)/d*100,2))
    else:
        out[k]=dict(calc=None, label=LAB[k], dev=None)
    print(k, out[k])
json.dump(out, open('dims.json','w'), indent=1)
print('total', sum(LAB.values()))
