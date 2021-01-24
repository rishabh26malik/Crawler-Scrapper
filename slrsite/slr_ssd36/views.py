from django.shortcuts import render
from django.http import HttpResponse, FileResponse, Http404
from django.template import loader
import json, asyncio, shutil, time
from .utils.iterative_ieee import get_ieee_results
from .utils.acm_with_file_handling import get_acm_results
from .utils.sd_probable_final import get_sciencedirect_results
from .utils.springer_with_file_handling import get_springer_results


# Create your views here.
def index(request):
    return render(request, 'slr_ssd36/index.html')


async def search(request):
    start = time.time()

    # only reply if the request is POST
    if request.method == 'POST':
        print('Post request received')
        print(json.loads(request.body))

        # converting string request to json
        query = json.loads(request.body)
        print(request.headers['X-CSRFToken'])

        # naming folder that citations with a unique name with use of CSRFToken
        # to avoid overwriting from multiple users.
        folder_name = 'citations'+request.headers['X-CSRFToken'] 

        # spawning threads for fetching from each of libraries.
        await asyncio.gather(*[
            get_acm_results(query["acmQuery"], folder_name), 
            get_ieee_results(query["ieeeQuery"], folder_name), 
            get_sciencedirect_results(query["sdQuery"], folder_name),
            get_springer_results(query["springerQuery"], folder_name)
            ])

        # making a zip file of all the citations.
        shutil.make_archive(folder_name, 'zip', folder_name)
    
        end = time.time()
        print("TOTAL TIME TAKEN: ", end-start)
    
        # preparing and sending citations zip as response
        file_resp = FileResponse(open(f"{folder_name}.zip", "rb"), as_attachment=True)
        file_resp['Content-Disposition'] = f'attachment; filename="{folder_name}.zip"'
        return file_resp

    # sending 404 error if request is not POST
    else:
        return Http404("Need to make POST request to /search")